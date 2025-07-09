import streamlit as st
import boto3
import os
import zipfile
import tempfile
import pandas as pd
import cv2

# Configuration
BUCKET_NAME = 'smartais-user-walks'
FRAME_IDS = [240, 1072]  # Default frame IDs

s3 = boto3.client('s3')


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


def get_frame_timestamp(video_path, frame_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_id >= total_frames:
        return None
    return round(frame_id / fps, 3)


def process_videos(folder_path, tester, walk_name, frame_ids):
    results = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                video_path = os.path.join(root, file)
                for frame_id in frame_ids:
                    ts = get_frame_timestamp(video_path, frame_id)
                    if ts is not None:
                        results.append([tester, walk_name, file, frame_id, ts])
    return results


# Streamlit UI
st.title("🎬 Frame Timestamp Extractor")

devices = list_devices()
selected_device = st.selectbox("Select Tester/Device", devices)

if selected_device:
    zips = list_zips(selected_device)
    selected_zips = st.multiselect("Select Walk ZIP(s)", zips)

    frame_input = st.text_input("Enter frame IDs (comma-separated)", value="240,1072")
    frame_ids = [int(f.strip()) for f in frame_input.split(',') if f.strip().isdigit()]

    if st.button("Process Selected Walks"):
        all_results = []
        for zip_key in selected_zips:
            walk_name = os.path.basename(zip_key).replace('.zip', '')
            st.write(f"🔄 Processing: `{walk_name}`")

            extracted_path = download_and_extract(zip_key)
            results = process_videos(extracted_path, selected_device, walk_name, frame_ids)
            all_results.extend(results)

        if all_results:
            df = pd.DataFrame(all_results, columns=["tester", "walk", "video", "frame_id", "timestamp"])
            st.success("✅ Processing complete!")
            st.dataframe(df)

            csv = df.to_csv(sep='\t', index=False).encode('utf-8')
            st.download_button("💾 Download Results CSV", csv, "Results.csv", "text/csv")
        else:
            st.warning("⚠️ No valid videos or frames found in selected ZIPs.")
