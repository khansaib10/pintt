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

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Pinterest links (shortlinks or full pin URLs)
PINTEREST_LINKS = [
    "https://pin.it/3Ez985TeB",
    # add more links here
]

# --- Helper: Resolve media URL ---
def get_media_url(url):
    """
    Resolve a Pinterest URL to a direct media URL (video or image).
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text

        # 1) Try to extract a direct video URL via regex
        video_match = re.search(r"https://v\.pinimg\.com/videos/[^"]+?\.mp4", html)
        if video_match:
            video_url = video_match.group(0)
            print(f"[+] Found video URL: {video_url}")
            return video_url, 'video'

        # 2) Fallback: check og:video meta
        soup = BeautifulSoup(html, 'html.parser')
        meta_video = soup.find('meta', property='og:video')
        if meta_video and meta_video.get('content'):
            print(f"[+] Found og:video: {meta_video['content']}")
            return meta_video['content'], 'video'

        # 3) Fallback: check og:image meta
        meta_image = soup.find('meta', property='og:image')
        if meta_image and meta_image.get('content'):
            print(f"[+] Found og:image: {meta_image['content']}")
            return meta_image['content'], 'image'

        print("[-] No media URL found on the Pinterest page.")
        return None, None
    except Exception as e:
        print(f"[-] Error resolving Pinterest URL: {e}")
        return None, None

# --- Download media ---
def download_media(url, kind):
    """
    Download media from URL, save with correct extension.
    """
    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        resp.raise_for_status()
        ext = '.mp4' if kind == 'video' else '.jpg'
        fname = f"temp{ext}"
        with open(fname, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        size = os.path.getsize(fname)
        print(f"[+] Downloaded {kind} ({size} bytes) to {fname}")
        return fname
    except Exception as e:
        print(f"[-] Error downloading media: {e}")
        return None

# --- Upload to Facebook ---
def upload_to_facebook(path, kind, caption):
    """
    Upload downloaded media to Facebook Page.
    """
    endpoint = (
        f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos" if kind == 'video'
        else f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos"
    )
    data = {
        'access_token': FB_PAGE_TOKEN,
        'description' if kind == 'video' else 'message': caption
    }
    files = {'source': open(path, 'rb')}
    print(f"[*] Uploading {kind} to Facebook...")
    try:
        resp = requests.post(endpoint, files=files, data=data)
        print(f"[+] Facebook response: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"[-] Error uploading to Facebook: {e}")

# --- Main Logic ---
def main():
    link = random.choice(PINTEREST_LINKS)
    print(f"[+] Picked link: {link}")
    media_url, kind = get_media_url(link)
    if not media_url:
        print("[-] Skipping: no media URL found.")
        return
    caption = random.choice(KEYWORDS)
    media_file = download_media(media_url, kind)
    if media_file:
        upload_to_facebook(media_file, kind, caption)
        os.remove(media_file)
    else:
        print("[-] Skipping upload due to download failure.")

if __name__ == '__main__':
    main()
