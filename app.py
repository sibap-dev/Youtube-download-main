from flask import Flask, render_template, request, send_file, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
progress_status = {"progress": "", "error": ""}  # Global status to share with frontend

# Progress hook function
def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('_percent_str', '0.0%').strip()
        progress_status['progress'] = downloaded
    elif d['status'] == 'finished':
        progress_status['progress'] = 'Download complete'
    elif d['status'] == 'error':
        progress_status['error'] = 'Download failed'

# Function to download video
def download_youtube_video(url):
    try:
        ydl_opts = {
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'format': 'best',
            'progress_hooks': [progress_hook]
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        progress_status['error'] = f"Download failed: {str(e)}"
        return None

# Route for frontend
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        progress_status['progress'] = ""
        progress_status['error'] = ""
        video_url = request.form.get("video_url")
        if video_url:
            file_path = download_youtube_video(video_url)
            if file_path:
                return send_file(file_path, as_attachment=True)
            else:
                return "❌ Error: Unable to download the video."
        else:
            return "❗ Please enter a valid YouTube URL."
    return render_template("index.html")

# Route for polling progress
@app.route("/progress")
def get_progress():
    return jsonify(progress_status)

# Ensure tmp folder exists
if not os.path.exists("/tmp"):
    os.makedirs("/tmp")

# Final deployment-friendly run configuration
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use PORT from Render or default 10000
    app.run(host='0.0.0.0', port=port)