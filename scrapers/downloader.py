# downloader.py

import requests
import os
from urllib.parse import urlparse

def download_video(video_url, target_folder, referer=None):
    """
    Mengunduh file video dari URL sumber ke folder target.
    Mendukung header 'Referer' kustom.
    Mengembalikan path file lokal jika sukses, None jika gagal.
    """
    
    try:
        # 1. Buat folder target jika belum ada
        os.makedirs(target_folder, exist_ok=True)
        
        # 2. Tentukan nama file lokal dari URL
        a = urlparse(video_url)
        # Ambil nama file dari path (misal: /video/abc.mp4?xyz -> abc.mp4)
        nama_file = os.path.basename(a.path).split('?')[0]
        if not nama_file: # Jika URL tidak jelas, beri nama default
            nama_file = "downloaded_video.mp4"
        
        local_file_path = os.path.join(target_folder, nama_file)

        # 3. Siapkan headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        
        # 4. KUNCI UTAMA: Tambahkan Referer jika disediakan
        if referer:
            headers['Referer'] = referer
            print(f"  Downloading (dengan Referer: {referer}) dari {video_url}...")
        else:
            print(f"  Downloading (normal) dari {video_url}...")

        # 5. Download file menggunakan stream=True (efisien untuk file besar)
        with requests.get(video_url, headers=headers, stream=True) as r:
            r.raise_for_status() # Cek error HTTP (404, 403, dll.)
            
            with open(local_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        
        print(f"  Download SUKSES. Tersimpan di: {local_file_path}")
        return local_file_path # Berhasil!
        
    except requests.exceptions.RequestException as e:
        print(f"  Downloader ERROR: Gagal men-download {video_url}. Detail: {e}")
        return None # Gagal
    except Exception as e:
        print(f"  Downloader ERROR: Terjadi kesalahan. Detail: {e}")
        return None # Gagal
