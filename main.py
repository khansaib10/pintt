import os
import random
import requests
from bs4 import BeautifulSoup

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

# --- Function to check and get the actual media from Pinterest ---
def get_media_url(url):
    try:
        # Fetch the page content
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the page content
        soup = BeautifulSoup(response.text, "html.parser")

        # Check if the page contains a video URL
        video_url = soup.find("meta", property="og:video")
        if video_url:
            print(f"[+] Found video: {video_url['content']}")
            return video_url["content"]

        # Otherwise, check for image URL
        image_url = soup.find("meta", property="og:image")
        if image_url:
            print(f"[+] Found image: {image_url['content']}")
            return image_url["content"]

        print("[-] No video or image found on the page.")
        return None
    except Exception as e:
        print(f"[-] Error fetching media from Pinterest: {e}")
        return None

# --- Download media (video or image) ---
def download_media(url, filename="media"):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            # Determine file extension
            file_extension = ".mp4" if url.endswith(".mp4") else ".jpg"
            filename = filename + file_extension
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"[+] Downloaded media to {filename}")
            return filename
        else:
            print(f"[-] Failed to download media: {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Error downloading media: {e}")
        return None

# --- Upload media to Facebook ---
def upload_to_facebook(media_path, caption, is_video=False):
    try:
        print("[*] Uploading media to Facebook...")

        url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/videos" if is_video else f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
        files = {'source': open(media_path, 'rb')}
        data = {
            'access_token': FB_PAGE_TOKEN,
            'description': caption
        }

        response = requests.post(url, files=files, data=data)
        print(f"[+] Facebook upload response: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"[-] Error uploading to Facebook: {e}")

# --- Main Bot Logic ---
def run_bot():
    # Hardcoded Pinterest URL for testing (this can be updated or fetched dynamically)
    pinterest_link = "https://pin.it/3Ez985TeB"  # Use any Pinterest link for testing
    
    # Get the actual media (either video or image)
    media_url = get_media_url(pinterest_link)
    if media_url:
        # Pick random caption
        caption = random.choice(KEYWORDS)

        # Download media
        media_file = download_media(media_url)

        if media_file:
            # Check if the media is a video or image by its extension
            is_video = media_file.endswith(".mp4")
            
            # Upload to Facebook (upload video or photo depending on file type)
            upload_to_facebook(media_file, caption, is_video)

            # Clean up downloaded file
            os.remove(media_file)
        else:
            print("[-] No media file downloaded.")
    else:
        print("[-] No valid media found.")

if __name__ == "__main__":
    run_bot()
