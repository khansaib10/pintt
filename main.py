import os
import random
import requests
from playwright.sync_api import sync_playwright
import re

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

# --- Functions ---

def pick_video():
    # For now, pick a random keyword
    keyword = random.choice(KEYWORDS)
    print(f"[+] Searching Pinterest for: {keyword}")
    return keyword

def get_video_url_from_pinterest(pin_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(pin_url)
            page.wait_for_selector('video')  # Wait for the video to be loaded

            # Extract video URLs from the page's JavaScript code
            page_content = page.content()
            video_urls = re.findall(r'https://[^\s]+\.mp4', page_content)
            if video_urls:
                video_url = video_urls[0]
                print(f"[+] Found video URL: {video_url}")
                browser.close()
                return video_url
            else:
                print("[-] No valid video found on this pin.")
                browser.close()
                return None
    except Exception as e:
        print(f"[-] Error extracting video from Pinterest: {e}")
        return None

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
    keyword = pick_video()

    # Searching Pinterest for the first result (you can extend this later for more random pins)
    pin_url = f"https://www.pinterest.com/search/pins/?q={keyword}"
    
    video_url = get_video_url_from_pinterest(pin_url)
    
    if video_url:
        video_file = download_video(video_url)

        if video_file:
            file_size = os.path.getsize(video_file)
            if file_size > 100 * 1024:  # Minimum 100 KB file size check
                upload_to_facebook(video_file, keyword)
            else:
                print("[-] Video too small, skipping upload.")
            os.remove(video_file)
        else:
            print("[-] No video file to upload.")
    else:
        print("[-] No valid video found, skipping this pin.")

if __name__ == "__main__":
    run_bot()
