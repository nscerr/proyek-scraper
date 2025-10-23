import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin 
from dateutil import parser as date_parser

def format_tanggal(datestring):
    if not datestring or datestring == "N/A":
        return "N/A"
    try:
        dt_obj = date_parser.parse(datestring)
        return dt_obj.strftime("%d %B %Y, %H:%M")
    except Exception as e:
        return datestring

def scrape(url_postingan):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    # Langkah 1
    try:
        response_html = requests.get(url_postingan, headers=headers)
        response_html.raise_for_status() 
        html_konten = response_html.text
    except requests.exceptions.RequestException as e:
        return {"error": f"Langkah 1 Gagal (HTML): {e}"}

    soup = BeautifulSoup(html_konten, 'html.parser')
    meta_tag = soup.find('meta', {'property': 'og:video:secure_url'})
    if not meta_tag:
        meta_tag = soup.find('meta', {'property': 'og:video'})

    if not meta_tag or not meta_tag.has_attr('content'):
        return {"error": "Langkah 1 Gagal (Tidak menemukan meta tag video)"}
        
    embed_url = meta_tag['content']

    # Langkah 2
    try:
        video_id = embed_url.split('/')[-1]
        if not video_id:
            return {"error": "Langkah 2 Gagal (Ekstrak ID)"}

        api_url = f"https://bestgore.fun/api/v1/videos/{video_id}"
        response_api = requests.get(api_url, headers=headers)
        response_api.raise_for_status()
        json_data = response_api.json()
        
    except Exception as e:
        return {"error": f"Langkah 2 Gagal (API): {e}"}

    # Langkah 3
    judul_artikel = json_data.get('name', "Judul Tidak Ditemukan")
    total_views = json_data.get('views', "Views Tidak Ditemukan")
    isi_artikel = json_data.get('description', "Deskripsi Tidak Ditemukan")
    
    tanggal_created = format_tanggal(json_data.get('createdAt', "N/A"))
    tanggal_updated = format_tanggal(json_data.get('updatedAt', "N/A"))
    tanggal_published = format_tanggal(json_data.get('publishedAt', "N/A"))

    url_video = "URL Video Tidak Ditemukan"
    resolusi_terbaik = 0
    
    streaming_playlists = json_data.get('streamingPlaylists', [])
    files_list = [] 
    
    if streaming_playlists:
        files_list = streaming_playlists[0].get('files', [])
    
    if files_list:
        for file_data in files_list:
            resolusi = file_data.get('resolution', {}).get('id', 0)
            file_url = file_data.get('fileUrl')
            if resolusi > resolusi_terbaik and file_url:
                resolusi_terbaik = resolusi
                url_video = file_url

    return {
        "source_site": "bestgore",
        "title": judul_artikel,
        "views": total_views,
        "description": isi_artikel,
        "created_at": tanggal_created,
        "updated_at": tanggal_updated,
        "published_at": tanggal_published,
        "video_urls": [url_video],
        "video_resolution": f"{resolusi_terbaik}p"
    }
