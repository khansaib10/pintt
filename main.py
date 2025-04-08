import os
import random
import re
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
KEYWORDS = [
    "luxury cars",
    "cars lovers",
    "car drifting",
    "Harley Davidson",
    "cars"
]

FB_PAGE_ID = os.environ.get("61574921212526")
FB_PAGE_TOKEN = os.environ.get("EAAySsQUbT7kBO4QrF6m5m4ZBwAXnTDw70GMuCsZCnhFuZARz6sSVmIXyRZByRQrMRaZCXZAHNglSMymV8qIC6W6e1CtJBfM4M3cnZBB16qj78bYPeGlIZCPhsPVcEPfbNnpZCGl0sP6wwi2xsooHrW11ozlLzwIrYvibU7SWZBcY6ds4juwsvzSOOjVhnW")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# --- Step 1: Search Pinterest for Pins ---
def search_pinterest(keyword):
    query = keyword.replace(" ", "%20")
    url = f"https://www.pinterest.com/search/pins/?q={query}"
    print(f"[+] Searching Pinterest for: {keyword} — {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        pins = re.findall(r'"(https://www\.pinterest\.com/pin/\d+/)"', response.text)
        pins = list(set(pins))  # remove duplicates
        print(f"[+] Found {len(pins)} pins")
        return pins
    except Exception as e:
        print("[-] Error searching Pinterest:", e)
        return []

# --- Step 2: Extract Video URL and Caption from Pin ---
def extract_video_info(pin_url):
    print(f"[>] Trying pin: {pin_url}")
    try:
        html = requests.get(pin_url, headers=HEADERS, timeout=15).text
        soup = BeautifulSoup(html, 'html.parser')

        # Extract video URL
        match = re.search(r'"video_list":\{.*?"url":"(https:\\/\\/v\.pinimg\.com.*?)"', html)
        video_url = match.group(1).replace('\\u002F', '/').replace('\\', '') if match else None

        # Extract caption
        title = soup.find("meta", property="og:description")
        caption = title["content"] if title else "🔥 Awesome Car Reel!"

        print(f"[+] Video URL: {video_url}")
        print(f"[+] Caption: {caption}")
        return video_url, caption
    except Exception as e:
        print("[-] Error extracting video info:", e)
        return None, None

# --- Step 3: Download Video ---
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

# --- Step 4: Upload to Facebook Page ---
def upload_to_facebook(video_path, caption):
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
    keyword = random.choice(KEYWORDS)
    pins = search_pinterest(keyword)
    
    for pin in pins:
        video_url, caption = extract_video_info(pin)
        if video_url:
            video_file = download_video(video_url)
            if video_file:
                upload_to_facebook(video_file, caption)
                break  # Success
    else:
        print("[-] No valid videos found.")

if __name__ == "__main__":
    run_bot()
