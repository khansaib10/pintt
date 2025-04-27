import os
import random
import requests
import mimetypes

# --- Configuration ---
FB_PAGE_ID    = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

# Your Pinterest links (could be video or image, no extension)
PINTEREST_LINKS = [
    "https://pin.it/3Ez985TeB",  # example shortlink
    # add more links here
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def pick_link():
    url = random.choice(PINTEREST_LINKS)
    print(f"[+] Picked link: {url}")
    return url

def download_content(url):
    """Download the URL, detect content-type, and save with the correct extension."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"[-] Download error: {e}")
        return None, None

    ctype = resp.headers.get("Content-Type", "").split(";")[0]
    ext = mimetypes.guess_extension(ctype) or ""
    if not ext:
        # fallback: image if startswith image, else video
        if ctype.startswith("image/"):
            ext = ".jpg"
        elif ctype.startswith("video/"):
            ext = ".mp4"
        else:
            ext = ""

    filename = f"temp{ext}"
    try:
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        size = os.path.getsize(filename)
        print(f"[+] Downloaded {ctype} ({size} bytes) to {filename}")
        return filename, ctype
    except Exception as e:
        print(f"[-] Save error: {e}")
        return None, None

def upload_to_facebook(path, ctype, caption):
    """Choose photos or videos endpoint based on content-type."""
    if ctype.startswith("image/"):
        endpoint = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos"
        data = {
            "access_token": FB_PAGE_TOKEN,
            "message": caption
        }
    elif ctype.startswith("video/"):
        endpoint = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        data = {
            "access_token": FB_PAGE_TOKEN,
            "description": caption
        }
    else:
        print(f"[-] Unsupported content type: {ctype}")
        return

    files = {"source": open(path, "rb")}
    print(f"[*] Uploading to Facebook ({'photos' if 'photos' in endpoint else 'videos'})...")
    try:
        resp = requests.post(endpoint, files=files, data=data)
        print(f"[+] Facebook response: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"[-] Upload error: {e}")

def main():
    link = pick_link()
    caption = "Check this out!"  # or random.choice(KEYWORDS) if you have keywords
    file_path, ctype = download_content(link)
    if file_path and ctype:
        upload_to_facebook(file_path, ctype, caption)
        os.remove(file_path)
    else:
        print("[-] Skipping upload due to download failure.")

if __name__ == "__main__":
    main()
