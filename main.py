import os
import random
import requests
import mimetypes
from bs4 import BeautifulSoup

# --- Configuration ---
FB_PAGE_ID    = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

# Your Pinterest links (could be short‐links or direct media URLs)
PINTEREST_LINKS = [
    "https://pin.it/3Ez985TeB",  # Pinterest shortlink example
    # add more links here
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# --- Helpers ---
def resolve_pinterest_url(url):
    """
    Follow a Pinterest shortlink or pin page, parse HTML for direct media URL.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Try video first
        meta = soup.find('meta', property='og:video')
        if meta and meta.get('content'):
            return meta['content']
        # Fallback to image
        meta = soup.find('meta', property='og:image')
        if meta and meta.get('content'):
            return meta['content']
        # Try canonical link as fallback
        link = soup.find('link', rel='canonical')
        if link and link.get('href'):
            return link['href']
    except Exception as e:
        print(f"[-] Error resolving Pinterest URL: {e}")
    return None

# --- Download and detect content ---
def download_content(url):
    """
    Download the URL, detect content-type, and save with proper extension.
    """
    # If Pinterest shortlink or page, resolve to media URL
    if 'pin.it' in url or 'pinterest.com' in url:
        resolved = resolve_pinterest_url(url)
        if not resolved:
            print(f"[-] Could not resolve Pinterest URL: {url}")
            return None, None
        url = resolved
        print(f"[+] Resolved to media URL: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[-] Download error: {e}")
        return None, None

    ctype = resp.headers.get('Content-Type', '').split(';')[0]
    ext = mimetypes.guess_extension(ctype) or ''
    if not ext:
        if ctype.startswith('image/'):
            ext = '.jpg'
        elif ctype.startswith('video/'):
            ext = '.mp4'
    filename = f"temp{ext}"

    try:
        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        size = os.path.getsize(filename)
        print(f"[+] Downloaded {ctype} ({size} bytes) to {filename}")
        return filename, ctype
    except Exception as e:
        print(f"[-] Save error: {e}")
        return None, None

# --- Upload to Facebook ---
def upload_to_facebook(path, ctype, caption):
    """
    Upload file to Facebook Page, choosing endpoint based on content-type.
    """
    if ctype.startswith('image/'):
        endpoint = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/photos"
        data = {'access_token': FB_PAGE_TOKEN, 'message': caption}
    elif ctype.startswith('video/'):
        endpoint = f"https://graph-video.facebook.com/v18.0/{FB_PAGE_ID}/videos"
        data = {'access_token': FB_PAGE_TOKEN, 'description': caption}
    else:
        print(f"[-] Unsupported content type: {ctype}")
        return

    files = {'source': open(path, 'rb')}
    print(f"[*] Uploading to Facebook ({'photos' if 'photos' in endpoint else 'videos'})...")
    try:
        resp = requests.post(endpoint, files=files, data=data)
        print(f"[+] Facebook response: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"[-] Upload error: {e}")

# --- Main Bot Logic ---
def main():
    url = random.choice(PINTEREST_LINKS)
    print(f"[+] Picked link: {url}")
    caption = "Check this out!"

    file_path, ctype = download_content(url)
    if file_path and ctype:
        upload_to_facebook(file_path, ctype, caption)
        os.remove(file_path)
    else:
        print("[-] Skipping upload due to download failure.")

if __name__ == '__main__':
    main()
