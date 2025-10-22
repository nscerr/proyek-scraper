import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape(url_postingan):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url_postingan, headers=headers)
        response.raise_for_status() 
        html_konten = response.text
    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengambil HTML: {e}"}

    soup = BeautifulSoup(html_konten, 'html.parser')
    video_container = soup.find('div', {'class': 'video-container'})
    
    judul_artikel = "Judul Tidak Ditemukan"
    info_upload = "Info Upload Tidak Ditemukan"
    url_video = "URL Video Tidak Ditemukan" # Nanti diubah jadi list

    if video_container:
        judul_element = video_container.find('h3')
        if judul_element:
            judul_artikel = judul_element.text.strip()
        
        info_element = video_container.find('div', {'class': 'about-video'})
        if info_element:
            info_upload = ' '.join(info_element.text.split())
            
        video_tag = video_container.find('video')
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and source_tag.has_attr('src'):
                video_src = source_tag['src']
                url_video = urljoin(url_postingan, video_src)
    
    # Kembalikan data sebagai dictionary
    return {
        "situs": "kaotic",
        "judul": judul_artikel,
        "info_upload": info_upload,
        "video_urls": [url_video] # Jadikan list agar konsisten
    }
