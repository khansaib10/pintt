import os
import random
import requests
import re
from bs4 import BeautifulSoup

# --- Configuration ---
KEYWORDS = [
    "luxury cars",
    "cars lovers",
    "bike reels",
    "car drifting",
    "Harley Davidson"
]

# Read from environment (GitHub Secrets)
FB_PAGE_ID    = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Your Pinterest links (shortlinks or full pin URLs)
PINTEREST_LINKS = [
    "https://pin.it/3Ez985TeB",
    # add more links here if you want
]

def get_media_url(page_url):
    """
    Resolve a Pinterest URL (pin page or shortlink) to a direct media URL.
    Returns (media_url, kind) where kind is 'video' or 'image'.
    """
    try:
        resp = requests.get(page_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text

        # 1) Try to extract a Pinterest CDN video link via regex
        video_match = re.search(r'https://v\.pinimg\.com/videos/[^"]+?\.mp4', html)
        if video_match:
            video_url = video_match.group(0)
            print(f"[+] Found video URL: {video_url}")
            return video_url, 'video'

        # 2) Fallback to OG video meta tag
        soup = BeautifulSoup(html, 'html.parser')
        meta_video = soup.find('meta', property='og:video')
        if meta_video and meta_video.get('content'):
            print(f"[+] Found og:video: {meta_video['content']}")
            return meta_video['content'], 'video'

        # 3) Fallback to OG image meta tag
        meta_image = soup.find('meta', property='og:image')
        if meta_image and meta_image.get('content'):
            print(f"[+] Found og:image: {meta_image['content']}")
            return meta_image['content'], 'image'

        print("[-] No media URL found on the Pinterest page.")
    except Exception as e:
        print(f"[-] Error resolving Pinterest URL: {e}")
    return None, None

def download_media(media_url, kind):
    """
    Download the media (video or image) and save it with the correct extension.
    Returns the local filename or None on error.
    """
    try:
        resp = requests.get(media_url, headers=HEADERS, stream=True, timeout=30)
        resp.raise_for_status()

        ext = '.mp4' if kind == 'video' else '.jpg'
        filename = f"temp{ext}"
        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)

        size = os.path.getsize(filename)
        print(f"[+] Downloaded {kind} ({size} bytes) to {filename}")
        return filename
    except Exception as e:
        print(f"[-] Error downloading media: {e}")
        return None

def upload_to_facebook(filepath, kind, caption):
    """
    Upload the downloaded file to Facebook Page.
    Uses the /videos endpoint for videos, /photos for images.
    """
    if kind == 'video':
        endpoint = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        data = {'access_token': FB_PAGE_TOKEN, 'description': caption}
    else:
        endpoint = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos"
        data = {'access_token': FB_PAGE_TOKEN, 'message': caption}

    files = {'source': open(filepath, 'rb')}
    print(f"[*] Uploading {kind} to Facebook...")
    try:
        resp = requests.post(endpoint, files=files, data=data)
        print(f"[+] Facebook response: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"[-] Error uploading to Facebook: {e}")

def main():
    link = random.choice(PINTEREST_LINKS)
    print(f"[+] Picked link: {link}")

    media_url, kind = get_media_url(link)
    if not media_url:
        print("[-] Skipping: no media URL found.")
        return

    caption = random.choice(KEYWORDS)
    media_file = download_media(media_url, kind)
    if not media_file:
        print("[-] Skipping upload due to download failure.")
        return

    upload_to_facebook(media_file, kind, caption)
    os.remove(media_file)

if __name__ == '__main__':
    main()
