import streamlit as st
import cv2
import tempfile
import os

st.title("🎞️ Frame Timestamp Finder")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
frame_id = st.number_input("Enter frame ID", min_value=0, step=1)

def get_frame_time(video_path, frame_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file.")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if frame_id >= total_frames:
        raise ValueError(f"Frame ID {frame_id} is out of range. Total frames: {total_frames}")
    
    return frame_id / fps

if uploaded_file and st.button("Get Timestamp"):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(uploaded_file.read())
            temp_video_path = temp_video.name
        
        timestamp = get_frame_time(temp_video_path, frame_id)
        st.success(f"✅ Frame {frame_id} occurs at **{timestamp:.3f} seconds**")

    except ValueError as e:
        st.error(f"❌ {e}")
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
