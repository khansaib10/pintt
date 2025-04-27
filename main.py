import os
import requests

# ————————————— Configuration ——————————————
FB_PAGE_ID    = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
HEADERS       = {"User-Agent": "Mozilla/5.0"}

# Replace this with your direct Pexels video URL
LINKS = [
    "https://videos.pexels.com/video-files/31721674/13515279_1080_1920_30fps.mp4"
]

def download_and_upload(url):
    print(f"[+] Downloading: {url}")
    r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
    r.raise_for_status()

    path = "test.mp4"
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    size = os.path.getsize(path)
    print(f"[+] Downloaded {size} bytes")

    if size < 1024:
        print("[-] File too small, aborting.")
        return

    upload_url = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
    files = {"source": open(path, "rb")}
    data  = {
        "access_token": FB_PAGE_TOKEN,
        "description": "Test upload from Pexels link"
    }
    print(f"[*] Uploading to Facebook…")
    resp = requests.post(upload_url, files=files, data=data)
    print(f"[+] Facebook response: {resp.status_code}")
    print(resp.json())

    os.remove(path)

if __name__ == "__main__":
    # since we only have one link, just run that
    download_and_upload(LINKS[0])
