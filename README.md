# 🛠️ Dev Tool Suite by Ananya Smart AIs

This repository contains a set of Streamlit-based tools developed to support video-based analysis and automation tasks. Each tool serves a specific, standalone purpose.

---

## 📦 Contents

| File                   | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `SDAnalyserApp.py`     | Analyzes walk session ZIPs stored in S3 and extracts timestamps for specific frame IDs. |
| `frame_timestamp_app.py` | Lightweight app that allows users to upload a single video file and get the timestamp of a specific frame. |

---

##  Tools Overview

### 1. `SDAnalyserApp.py` — Walk ZIP Frame Extractor

A tool designed for testers and researchers to process videos inside `.zip` archives from an S3 bucket and extract the exact timestamp of specified frame IDs.

#### 🔹 Features:
- Connects to AWS S3 (`smartais-user-walks`)
- Lists testers/devices and their `.zip` walk sessions
- Allows multiple ZIP selection and custom frame ID input
- Extracts timestamps from all matching videos
- Displays results in a table
- Option to download as `.csv`

#### 🔧 Dependencies:
- `streamlit`
- `boto3`
- `pandas`
- `opencv-python`

#### ▶️ Run:
```bash
streamlit run SDAnalyserApp.py

2. frame_timestamp_app.py — Single Video Frame Timestamp Finder
A lightweight and fast tool to find the timestamp of a specific frame in a manually uploaded video file.

🔹 Features:
Upload .mp4, .mov, or .avi videos

Input a frame ID

Instantly view the timestamp of that frame

Validates frame ID range

🔧 Dependencies:
streamlit

opencv-python

▶️ Run:

streamlit run frame_timestamp_app.py

🔧 Setup Instructions
Install dependencies:

pip install streamlit boto3 pandas opencv-python

Make sure your AWS credentials are set up if you plan to use SDAnalyserApp.py.


