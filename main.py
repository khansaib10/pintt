import os
import requests
from bs4 import BeautifulSoup

def search_pinterest_links():
    keywords = [
        "luxury cars",
        "cars lovers",
        "car drifting",
        "Harley Davidson",
        "cars"
    ]
    
    search_results = []
    for keyword in keywords:
        search_url = f"https://www.pinterest.com/search/pins/?q={keyword.replace(' ', '%20')}"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pins = soup.find_all('a', href=True)
            
            for pin in pins:
                if '/pin/' in pin['href']:
                    pin_url = "https://www.pinterest.com" + pin['href']
                    if pin_url not in search_results:
                        search_results.append(pin_url)
                        if len(search_results) >= 5:  # Limit results to avoid spam
                            return search_results
    
    return search_results

def extract_caption_from_pin(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('meta', property='og:description')
        caption = title['content'] if title else "🔥 Awesome Bike Reel!"
        return caption
    except Exception as e:
        print("Error extracting caption:", e)
        return "🔥 Awesome Bike Reel!"

def download_video(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open("video.mp4", "wb") as file:
                file.write(response.content)
            return "video.mp4"
        else:
            print("Download failed.")
            return None
    except Exception as e:
        print("Error downloading video:", e)
        return None

def upload_to_facebook(video_path, caption):
    fb_page_id = os.environ.get("61574921212526")
    fb_page_token = os.environ.get("EAAySsQUbT7kBO4QrF6m5m4ZBwAXnTDw70GMuCsZCnhFuZARz6sSVmIXyRZByRQrMRaZCXZAHNglSMymV8qIC6W6e1CtJBfM4M3cnZBB16qj78bYPeGlIZCPhsPVcEPfbNnpZCGl0sP6wwi2xsooHrW11ozlLzwIrYvibU7SWZBcY6ds4juwsvzSOOjVhnW")
    
    url = f"https://graph.facebook.com/v18.0/{fb_page_id}/videos"
    params = {
        "access_token": fb_page_token,
        "description": caption
    }
    files = {"source": open(video_path, "rb")}
    
    response = requests.post(url, files=files, data=params)
    print(response.json())
    
# Main execution
if __name__ == "__main__":
    pin_links = search_pinterest_links()
    
    for pin in pin_links:
        print(f"Trying: {pin}")
        caption = extract_caption_from_pin(pin)
        video_path = download_video(pin)  # This needs to be updated with actual video extraction logic
        
        if video_path:
            upload_to_facebook(video_path, caption)
