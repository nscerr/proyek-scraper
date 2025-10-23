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

    judul_artikel = "Judul Tidak Ditemukan"
    tanggal_terbit = "Tanggal Tidak Ditemukan"
    jumlah_views = "Views Tidak Ditemukan"
    isi_artikel = "Isi Artikel Tidak Ditemukan"
    list_url_video = []

    judul_element = soup.find('h1', class_='entry-title')
    if judul_element:
        judul_artikel = judul_element.text.strip()
        
    tanggal_element = soup.find('time', class_='entry-date published')
    if tanggal_element:
        tanggal_terbit = tanggal_element.text.strip()

    views_container = soup.find('span', class_='post-views')
    if views_container:
        count_element = views_container.find('span', class_='count')
        if count_element:
            jumlah_views = f"{count_element.text.strip()} views"
        else:
            jumlah_views = ' '.join(views_container.text.split())

    content_container = soup.find('div', {'itemprop': 'articleBody'})
    
    if content_container:
        semua_source_tags = content_container.find_all('source')
        if semua_source_tags:
            for source_tag in semua_source_tags:
                if source_tag.has_attr('src'):
                    video_src = source_tag['src']
                    list_url_video.append(urljoin(url_postingan, video_src))
        
        paragraf_list = content_container.find_all('p')
        if paragraf_list:
            isi_artikel = "\n\n".join([p.text.strip() for p in paragraf_list])
            
    if not list_url_video:
        list_url_video.append("URL Video Tidak Ditemukan")

    # Kembalikan data sebagai dictionary
    return {
        "source_site": "seegore",
        "title": judul_artikel,
        "publish_date": tanggal_terbit,
        "views": jumlah_views,
        "video_urls": list_url_video,
        "article_body": isi_artikel
    }
