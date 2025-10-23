# downloader.py (VERSI BARU: Nama Acak + Progress Hening)

import requests
import os
import string
import random
from urllib.parse import urlparse
from tqdm import tqdm

def download_video(video_url, target_folder, referer=None, quiet=False):
    """
    Mengunduh file video.
    Selalu menampilkan progress bar TQDM.
    Menyembunyikan log teks lain jika quiet=True.
    Menyimpan dengan 5 karakter acak.
    """
    
    try:
        os.makedirs(target_folder, exist_ok=True)
        
        # --- LOGIKA NAMA FILE BARU ---
        a = urlparse(video_url)
        nama_file_asli = os.path.basename(a.path).split('?')[0]
        # Dapatkan ekstensi (misal: ".mp4")
        _ , extension = os.path.splitext(nama_file_asli)
        # Buat 5 karakter acak (huruf kecil + angka)
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        # Gabungkan
        random_file_name = f"{random_suffix}{extension}"
        if not extension: # Jaga-jaga jika tidak ada ekstensi
           random_file_name = random_suffix
           
        local_file_path = os.path.join(target_folder, random_file_name)
        # --- AKHIR LOGIKA NAMA FILE ---

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        
        if referer:
            headers['Referer'] = referer
            if not quiet: # Log ini tetap menghormati mode hening
                print(f"  Downloading (dengan Referer: {referer}) dari {video_url}...")
        else:
            if not quiet: # Log ini tetap menghormati mode hening
                print(f"  Downloading (normal) dari {video_url}...")

        r = requests.get(video_url, headers=headers, stream=True)
        r.raise_for_status() 

        total_size_in_bytes = int(r.headers.get('content-length', 0))
        chunk_size = 8192

        # Progress bar TQDM sekarang SELALU tampil
        progress_bar = tqdm(
            total=total_size_in_bytes,
            desc=f"  -> {random_file_name} (Download)", # Tambahkan label
            unit='iB',
            unit_scale=True,
            leave=False
        )
        
        with open(local_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size): 
                progress_bar.update(len(chunk)) # Selalu update
                f.write(chunk)
        
        progress_bar.close() # Selalu tutup

        if not quiet: # Log ini tetap menghormati mode hening
            print(f"  Download SUKSES. Tersimpan di: {local_file_path}")
            
        return local_file_path
        
    except Exception as e:
        if not quiet: # Log ini tetap menghormati mode hening
            print(f"  Downloader ERROR: Gagal men-download {video_url}. Detail: {e}")
        if 'progress_bar' in locals():
            progress_bar.close()
        return None
