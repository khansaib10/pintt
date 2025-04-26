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

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

PINTEREST_VIDEOS = [
    "https://v.pinimg.com/videos/mc/720p/2e/35/6d/2e356d6612f1c53c3a5d6e7ababc7bb9.mp4",
    "https://v.pinimg.com/videos/mc/720p/79/4d/91/794d9179389b8e5e55c1a84bdc22ce64.mp4",
    "https://v.pinimg.com/videos/mc/720p/a1/62/b7/a162b7bc80c64e9a9e1d8e59ab22ce5b.mp4",
    "https://v.pinimg.com/videos/mc/720p/f3/ea/31/f3ea3104f9625e7f0c8b55c948450fe6.mp4",
    "https://v.pinimg.com/videos/mc/720p/6e/45/44/6e4544051f04be07e76bfcfa61e24a13.mp4"
]

# --- Step 1: Pick a random video ---
def pick_video():
    video_url = random.choice(PINTEREST_VIDEOS)
    caption = random.choice(KEYWORDS)
    print(f"[+] Picked video: {video_url}")
    print(f"[+] Caption: {caption}")
    return video_url, caption

# --- Step 2: Download Video ---
def download_video(url, filename="video.mp4"):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"[+] Downloaded video to {filename}")
        return filename
    except Exception as e:
        print("[-] Error downloading video:", e)
        return None

# --- Step 3: Upload to Facebook Page ---
def upload_to_facebook(video_path, caption):
    if not FB_PAGE_ID or not FB_PAGE_TOKEN:
        print("[-] ERROR: FB_PAGE_ID or FB_PAGE_TOKEN is missing!")
        return
    
    print("[*] Uploading video to Facebook...")
    try:
        url = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
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

# --- Main Bot Logic ---
def run_bot():
    video_url, caption = pick_video()
    video_file = download_video(video_url)
    if video_file:
        upload_to_facebook(video_file, caption)

if __name__ == "__main__":
    run_bot()
