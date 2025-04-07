import os
import requests
from bs4 import BeautifulSoup
import random
import re
import json

# --- Configuration ---
KEYWORDS = [
    "luxury cars",
    "cars lovers",
    "car drifting",
    "Harley Davidson",
    "cars"
]

FB_PAGE_ID = os.getenv("61574921212526")
FB_PAGE_TOKEN = os.getenv("EAAySsQUbT7kBO4QrF6m5m4ZBwAXnTDw70GMuCsZCnhFuZARz6sSVmIXyRZByRQrMRaZCXZAHNglSMymV8qIC6W6e1CtJBfM4M3cnZBB16qj78bYPeGlIZCPhsPVcEPfbNnpZCGl0sP6wwi2xsooHrW11ozlLzwIrYvibU7SWZBcY6ds4juwsvzSOOjVhnW")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# --- Step 1: Search Pinterest ---
def search_pinterest(keyword):
    query = keyword.replace(" ", "%20")
    url = f"https://www.pinterest.com/search/pins/?q={query}"
    print(f"Searching Pinterest for: {keyword}")
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    pins = re.findall(r'"(https://www\.pinterest\.com/pin/\d+/)"', response.text)
    return list(set(pins))  # unique pin links

# --- Step 2: Extract Video URL & Caption ---
def extract_video_info(pin_url):
    print(f"Trying: {pin_url}")
    try:
        html = requests.get(pin_url, headers=HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')

        # Extract video URL
        scripts = soup.find_all('script')
        for script in scripts:
            if 'video_list' in script.text:
                match = re.search(r'"video_list":\{.*?"url":"(.*?)"', script.text)
                if match:
                    video_url = match.group(1).replace('\\u002F', '/')
                    break
        else:
            return None, None

        # Extract caption
        title = soup.find("meta", property="og:description")
        caption = title["content"] if title else "🔥 Awesome Car Reel!"
        return video_url, caption
    except Exception as e:
        print("Error extracting video info:", e)
        return None, None

# --- Step 3: Download Video ---
def download_video(video_url, filename):
    try:
        print(f"Downloading video: {video_url}")
        response = requests.get(video_url)
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print("Video download failed:", e)
        return False

# --- Step 4: Upload to Facebook ---
def upload_to_facebook(video_path, caption):
    url = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
    files = {'source': open(video_path, 'rb')}
    data = {
        'access_token': FB_PAGE_TOKEN,
        'description': caption
    }
    response = requests.post(url, files=files, data=data)
    print("Facebook upload response:", response.text)
    return response.status_code == 200

# --- Main Flow ---
def main():
    keyword = random.choice(KEYWORDS)
    pins = search_pinterest(keyword)
    for pin in pins:
        video_url, caption = extract_video_info(pin)
        if video_url:
            video_file = "video.mp4"
            if download_video(video_url, video_file):
                if upload_to_facebook(video_file, caption):
                    print("✅ Successfully uploaded to Facebook!")
                    break
                else:
                    print("❌ Facebook upload failed.")
            else:
                print("❌ Video download failed.")
        else:
            print("❌ Could not extract video URL.")

if __name__ == "__main__":
    main()
