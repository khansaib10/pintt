import os
import random
import requests

# --- Configuration ---
KEYWORDS = [
    "luxury cars",
    "cars lovers",
    "bike reels",
    "car drifting",
    "Harley Davidson"
]

# Read from GitHub Secrets (environment variables)
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Hardcoded Pinterest video sources (you can replace these later)
PINTEREST_VIDEOS = [
    "https://pin.it/3Ez985TeB",
   
]

# --- Functions ---

def pick_video():
    video_url = random.choice(PINTEREST_VIDEOS)
    caption = random.choice(KEYWORDS)
    print(f"[+] Picked video: {video_url}")
    print(f"[+] Caption: {caption}")
    return video_url, caption

def download_video(url, filename="video.mp4"):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"[+] Downloaded video to {filename}")
            return filename
        else:
            print("[-] Failed to download video:", response.status_code)
            return None
    except Exception as e:
        print("[-] Error downloading video:", e)
        return None

def upload_to_facebook(video_path, caption):
    try:
        print("[*] Uploading video to Facebook...")

        url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/videos"
        files = {'source': open(video_path, 'rb')}
        data = {
            'access_token': FB_PAGE_TOKEN,
            'description': caption
        }

        response = requests.post(url, files=files, data=data)
        print(f"[+] Facebook upload response: {response.status_code}")
        print(response.json())
    except Exception as e:
        print("[-] Error uploading to Facebook:", e)

def run_bot():
    video_url, caption = pick_video()
    video_file = download_video(video_url)

    if video_file:
        file_size = os.path.getsize(video_file)
        if file_size > 100 * 1024:  # Minimum 100 KB file size check
            upload_to_facebook(video_file, caption)
        else:
            print("[-] Video too small, skipping upload.")
        os.remove(video_file)

if __name__ == "__main__":
    run_bot()
