import streamlit as st
import cv2
import numpy as np
from sklearn.ensemble import IsolationForest
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt

# ================= ALERT SOUND =================
def play_alert_sound():
    st.markdown("""
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

# ================= EMAIL ALERT =================
def send_email_alert(score):
    msg = EmailMessage()
    msg.set_content(f"""
ALERT: Deepfake Detected

Risk Score: {score}%
Action Taken: File Isolated
""")

    msg["Subject"] = "🚨 SOC ALERT: Deepfake Detected"
    msg["From"] = "santhoshkuppusamy19@gmail.com"
    msg["To"] = "anuradhasanthosh85@gmail.com"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("santhoshkuppusamy19@gmail.com", "santhoshsanthosh")
    server.send_message(msg)
    server.quit()

# ================= DEEPFAKE DETECTION =================
def detect_deepfake(video_path):
    cap = cv2.VideoCapture(video_path)
    diffs = []
    prev = None
    count = 0

    while cap.isOpened() and count < 40:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if prev is not None:
            diff = cv2.absdiff(prev, gray)
            diffs.append(np.mean(diff))

        prev = gray
        count += 1

    cap.release()

    if len(diffs) < 10:
        return "UNKNOWN", 0

    X = np.array(diffs).reshape(-1, 1)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.15,
        random_state=42
    )
    model.fit(X)

    preds = model.predict(X)
    anomaly_ratio = (preds == -1).sum() / len(preds)
    score = round(anomaly_ratio * 100, 2)

    if score > 45:
        return "FAKE", score
    else:
        return "REAL", score

# ================= STREAMLIT DASHBOARD =================
st.set_page_config(page_title="SOC Deepfake Detection", layout="centered")

st.title("🤖 AI Agent Based Deepfake Detection & SOC Alert System")
st.write("Upload a video to analyze (REAL vs DEEPFAKE)")

uploaded_video = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_video:
    with open("temp.mp4", "wb") as f:
        f.write(uploaded_video.read())

    st.video("temp.mp4")

    with st.spinner("AI Agent analyzing video..."):
        result, score = detect_deepfake("temp.mp4")

    st.subheader("🔍 Detection Result")

    if result == "FAKE":
        play_alert_sound()          # 🔊 SOUND
        send_email_alert(score)     # 📧 EMAIL
        st.error(f"🚨 FAKE Detected | Risk Score: {score}%")
        st.warning("SOC Action: Alert Sent & File Isolated")

    elif result == "REAL":
        st.success(f"✅ REAL Video | Risk Score: {score}%")

    else:
        st.info("⚠ Not enough data to analyze")

    # ===== Risk Meter =====
    st.subheader("📊 Risk Meter")
    st.progress(min(int(score), 100))

    if score < 30:
        st.success("Low Risk")
    elif score < 50:
        st.warning("Medium Risk")
    else:
        st.error("High Risk")

    # ===== Graph =====
    st.subheader("📈 Anomaly Distribution")
    fig, ax = plt.subplots()
    ax.bar(["Normal", "Anomaly"], [100 - score, score])
    ax.set_ylabel("Percentage")
    st.pyplot(fig)

    # ===== Incident Log =====
    st.subheader("🧾 Incident Log")
    st.write({
        "File": uploaded_video.name,
        "Status": result,
        "Risk Score": f"{score}%",
        "Action": "Isolated" if result == "FAKE" else "Allowed"
    })