# SDAnalyserApp 

**SDAnalyserApp** is a Streamlit-based tool for analyzing video frame timestamps in walk session videos stored on AWS S3. It allows testers or researchers to extract the timestamp for specific frame IDs from multiple uploaded videos within ZIP archives.

---

## Features

- Select a device (tester) from S3 folder structure
- Browse and select `.zip` files containing walk videos
- Input specific frame IDs to analyze
- Automatically downloads, extracts, and processes videos
- Extracts timestamp (in seconds) for specified frames
- Displays results in a table
- Option to download results as a `.csv` file

---

## 📁 Project Structure

- `SDAnalyserApp.py`: Main Streamlit app
- Uses:
  - `boto3` for S3 interaction
  - `cv2` (OpenCV) for frame-based timestamp extraction
  - `pandas` for tabular data display and export

---

##  How to Run

1. **Install dependencies** (you can use a virtual environment):
   ```bash
   pip install streamlit boto3 pandas opencv-python
   Run the app:

2. Run the app:
   
   streamlit run SDAnalyserApp.py
   
3.Use the interface:

- Select a tester/device
- Choose one or more ZIPs
- Enter desired frame IDs (e.g., 240,1072)
- Click "Process Selected Walks"
- View or download the results
