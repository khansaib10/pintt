# main.py

import os
import random
import asyncio
import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# --- Configuration ---
KEYWORDS = [
    "luxury cars",
    "bike reels",
    "Harley Davidson",
    "car drifting",
    "superbike girls",
]

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# --- Functions ---

async def search_pinterest(keyword):
    print(f"[*] Searching Pinterest for: {keyword}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        search_url = f"https://www.pinterest.com/search/pins/?q={keyword.replace(' ', '%20')}&rs=typed"
        await page.goto(search_url)
        await page.wait_for_timeout(3000)

        content = await page.content()
        await browser.close()
        
        soup = BeautifulSoup(content, "html.parser")
        pins = soup.find_all("a", href=True)

        video_pins = []
        for pin in pins:
            href = pin['href']
            if "/pin/" in href and href not in video_pins:
                video_pins.append("https://www.pinterest.com" + href)
        
        print(f"[+] Found {len(video_pins)} pins")
        return video_pins

async def extract_video_url(pin_url):
    print(f"[*] Extracting video from pin: {pin_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(pin_url)
        await page.wait_for_timeout(3000)

        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        video_tag = soup.find("video")
        if video_tag:
            source = video_tag.find("source")
            if source and source['src']:
                print(f"[+] Found video link: {source['src']}")
                return source['src']
    print("[-] No video found.")
    return None

def download_video(video_url, filename="video.mp4"):
    print(f"[*] Downloading video...")
    try:
        response = requests.get(video_url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"[+] Saved video to {filename}")
            return filename
        else:
            print("[-] Failed to download video:", response.status_code)
            return None
    except Exception as e:
        print("[-] Exception downloading video:", e)
        return None

def upload_to_facebook(video_path, caption):
    print("[*] Uploading video to Facebook...")
    try:
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

async def run_bot():
    keyword = random.choice(KEYWORDS)
    pins = await search_pinterest(keyword)

    for pin_url in pins:
        video_url = await extract_video_url(pin_url)
        if video_url:
            video_file = download_video(video_url)
            if video_file:
                file_size = os.path.getsize(video_file)
                if file_size > 100 * 1024:  # Minimum 100 KB
                    upload_to_facebook(video_file, keyword)
                    os.remove(video_file)
                    return  # success, stop here
                else:
                    print("[-] Video too small, trying next...")
                    os.remove(video_file)
            else:
                print("[-] Could not download video, trying next...")
        else:
            print("[-] No video found, trying next pin...")

    print("[-] No valid videos found for this keyword.")

# --- Main ---

if __name__ == "__main__":
    asyncio.run(run_bot())
