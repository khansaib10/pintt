import random
import requests
import subprocess
import os
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

# --- Step 1: Get Pinterest Video Links ---
def search_pinterest_links():
    return [
        "https://www.pinterest.com/pin/847240367256128875/",
        "https://www.pinterest.com/pin/847240367256129238/",
        "https://www.pinterest.com/pin/847240367256128912/"
    ]

# --- Step 2: Extract Caption from Pinterest Pin ---
def extract_caption_from_pin(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('meta', property='og:description')
        caption = title['content'] if title else "🔥 Awesome Bike Reel!"
    except Exception as e:
        print("Error extracting caption:", e)
        caption = "🔥 Awesome Bike Reel!"
    
    hashtags = " #BikeReels #Bikers #HarleyDavidson #BikeLovers #MotorcycleLife"
    return caption + hashtags

# --- Step 3: Download Video ---
def download_video(pinterest_url):
    filename = "video.mp4"
    try:
        subprocess.run([
            "yt-dlp", pinterest_url,
            "-o", filename,
            "--no-playlist",
            "--quiet",
            "--no-warnings"
        ], check=True)
        return filename
    except subprocess.CalledProcessError:
        print("Download failed.")
        return None

# --- Step 4: Upload to Facebook ---
def upload_to_facebook(video_path, caption):
    url = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
    with open(video_path, 'rb') as f:
        response = requests.post(
            url,
            files={'source': f},
            data={
                'access_token': FB_PAGE_TOKEN,
                'description': caption
            }
        )
    if response.status_code == 200:
        print("✅ Uploaded to Facebook!")
    else:
        print("❌ Upload failed:", response.text)

# --- Main Bot Flow ---
def main():
    print("🔍 Searching Pinterest...")
    links = search_pinterest_links()
    random.shuffle(links)
    for link in links:
        print(f"➡️ Trying: {link}")
        video_file = download_video(link)
        if video_file:
            caption = extract_caption_from_pin(link)
            upload_to_facebook(video_file, caption)
            os.remove(video_file)
            break

if __name__ == "__main__":
    main()
