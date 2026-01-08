import streamlit as st
import cv2
import numpy as np
import requests
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Deepfake Detection System",
    layout="centered"
)

st.title("🎭 Deepfake Detection Dashboard")
st.write("AI-based Video Analysis with Email Alert")

# ---------------- EMAIL ALERT (NO SMTP) ----------------
def send_email_alert(score):
    FORM_ENDPOINT = "https://formspree.io/f/mvzgelpd"  
    # 🔁 UN FORMSpree endpoint inga paste pannu

    data = {
        "email": "santhoshkuppyusamy19@gmail.com",
        "subject": "🚨 Deepfake Alert",
        "message": f"Fake video detected!\nRisk Score: {score}%"
    }

    try:
        r = requests.post(FORM_ENDPOINT, data=data)
        if r.status_code == 200:
            st.success("📧 Email alert sent successfully")
        else:
            st.error("❌ Email sending failed")
    except Exception as e:
        st.error(e)

# ---------------- DETECTION LOGIC (DEMO SAFE) ----------------
def detect_deepfake(video_path):
    cap = cv2.VideoCapture(video_path)
    blur_scores = []
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_scores.append(blur)

        count += 1
        if count > 25:
            break

    cap.release()

    avg_blur = np.mean(blur_scores)

    # Demo logic
    if avg_blur < 90:
        return "FAKE", 75
    else:
        return "REAL", 20

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📤 Upload a video file",
    type=["mp4", "avi", "mov"]
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        video_path = tmp.name

    with st.spinner("🔍 Analyzing video..."):
        result, risk = detect_deepfake(video_path)

    st.subheader("🧠 Detection Result")

    if result == "FAKE":
        st.error("⚠ FAKE VIDEO DETECTED")
        st.metric("Risk Score", f"{risk}%")
        send_email_alert(risk)
    else:
        st.success("✅ REAL VIDEO")
        st.metric("Risk Score", f"{risk}%")

st.markdown("---")
st.caption("Deepfake Detection | College Demo Project")

