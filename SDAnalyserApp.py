import streamlit as st
import boto3
import os
import zipfile
import tempfile
import pandas as pd
import cv2
from PIL import Image

# AWS S3 config
BUCKET_NAME = 'smartais'
s3 = boto3.client('s3')


# ---- Utilities ----

def list_devices():
    result = s3.list_objects_v2(Bucket=BUCKET_NAME, Delimiter='/')
    return [prefix['Prefix'].rstrip('/') for prefix in result.get('CommonPrefixes', [])]


def list_zips(device_prefix):
    result = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"{device_prefix}/")
    return [obj['Key'] for obj in result.get('Contents', []) if obj['Key'].endswith('.zip')]


def download_and_extract(zip_key):
    tmpdir = tempfile.mkdtemp()
    local_zip = os.path.join(tmpdir, os.path.basename(zip_key))
    s3.download_file(BUCKET_NAME, zip_key, local_zip)

    with zipfile.ZipFile(local_zip, 'r') as zip_ref:
        zip_ref.extractall(tmpdir)

    return tmpdir


def extract_frame_image(video_path, frame_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_id >= total_frames:
        return None
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
    success, frame = cap.read()
    cap.release()
    if success:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
    return None


def find_csv_and_video(folder_path):
    csv_path = None
    video_path = None
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f == "sceneDescriptionHistory.csv":
                csv_path = os.path.join(root, f)
            if f.lower().endswith(('.mp4', '.mov', '.avi')):
                video_path = os.path.join(root, f)
        if csv_path and video_path:
            break
    return csv_path, video_path


def parse_qna_from_csv(csv_path, video_path):
    df = pd.read_csv(csv_path)
    df = df[df['Question Asked'].notna() & df['AI Reply'].notna() & df['FrameID'].notna()]
    df = df.astype({'FrameID': 'int'})

    entries = []
    for _, row in df.iterrows():
        frame_id = row['FrameID']
        timestamp = row['TimeStamp']
        question = row['Question Asked']
        answer = row['AI Reply']
        image = extract_frame_image(video_path, frame_id)
        entries.append({
            "timestamp": timestamp,
            "frame_id": frame_id,
            "question": question,
            "answer": answer,
            "image": image
        })
    return entries


# ---- Streamlit UI ----

st.title("Smartais SD Q&A + Frame Image Verifier")

devices = list_devices()
selected_device = st.selectbox("Select Tester/Device", devices)

if selected_device:
    zip_keys = list_zips(selected_device)

    st.info("📦 Scanning for valid walks containing sceneDescriptionHistory.csv...")

    # Scan all zips to find valid ones with sceneDescriptionHistory.csv
    valid_walk_map = {}
    for zip_key in zip_keys:
        try:
            tmpdir = download_and_extract(zip_key)
            csv_path, video_path = find_csv_and_video(tmpdir)
            if csv_path and video_path:
                walk_name = os.path.basename(zip_key).replace(".zip", "")
                valid_walk_map[walk_name] = (zip_key, tmpdir, csv_path, video_path)
        except Exception:
            continue

    if not valid_walk_map:
        st.warning("⚠️ No valid walks with sceneDescriptionHistory.csv found.")
    else:
        selected_walk = st.selectbox("📁 Select a Walk to Review", list(valid_walk_map.keys()))

        if selected_walk:
            zip_key, folder_path, csv_path, video_path = valid_walk_map[selected_walk]
            st.subheader(f"🔍 Reviewing Walk: `{selected_walk}`")

            qna_entries = parse_qna_from_csv(csv_path, video_path)
            if not qna_entries:
                st.info("No valid Q&A entries found.")
            else:
                for entry in qna_entries:
                    st.markdown(f"🕒 **{entry['timestamp']}**")
                    st.markdown(f"❓ **Q:** {entry['question']}")
                    st.markdown(f"💬 **A:** {entry['answer']}")
                    if entry['image']:
                        st.image(entry['image'], caption=f"🖼️ Frame {entry['frame_id']}", use_column_width=True)
                    else:
                        st.warning(f"⚠️ Could not extract image for frame {entry['frame_id']}")

