# uploader.py (VERSI BARU: Progress Bar Upload + Mode Hening)

import requests
import os
import uuid
import mimetypes
from tqdm import tqdm
# --- IMPOR BARU UNTUK PROGRESS UPLOAD ---
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
# ----------------------------------------

MAX_SIZE_MB = 100
URL_ENDPOINT = "https://videy.co/api/upload"

def upload(local_file_path, quiet=False):
    """
    Meng-upload satu file video ke videy.co.
    Selalu menampilkan progress bar TQDM.
    Menyembunyikan log teks lain jika quiet=True.
    """
    
    if not os.path.exists(local_file_path):
        if not quiet:
            print(f"Uploader ERROR: File '{local_file_path}' tidak ditemukan.")
        return None
    
    file_size_bytes = os.path.getsize(local_file_path)
    max_size_bytes = MAX_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        if not quiet:
            print(f"Uploader ERROR: Ukuran file ({file_size_bytes / 1024 / 1024:.2f} MB) melebihi batas ({MAX_SIZE_MB} MB).")
        return None

    visitor_id = str(uuid.uuid4())
    full_url = f"{URL_ENDPOINT}?visitorId={visitor_id}"
    
    if not quiet: # Log ini tetap menghormati mode hening
        print(f"  Uploading '{os.path.basename(local_file_path)}' ke Videy.co...")

    try:
        # --- LOGIKA PROGRESS BAR UPLOAD BARU ---
        
        # 1. Siapkan TQDM bar
        nama_file = os.path.basename(local_file_path)
        progress_bar = tqdm(
            total=file_size_bytes,
            desc=f"  -> {nama_file} (Upload)", # Tambahkan label
            unit='iB',
            unit_scale=True,
            leave=False
        )

        # 2. Definisikan callback yang akan dipanggil saat upload
        def upload_callback(monitor):
            # Update bar dengan jumlah byte yang baru dibaca
            progress_bar.update(monitor.bytes_read - progress_bar.n)

        # 3. Buka file dan buat encoder
        with open(local_file_path, 'rb') as f:
            mime_type, _ = mimetypes.guess_type(local_file_path)
            if mime_type is None: mime_type = 'application/octet-stream'
            
            # Buat encoder multipart (ini menggantikan dict 'files')
            encoder = MultipartEncoder(
                fields={'file': (nama_file, f, mime_type)}
            )
            
            # Bungkus encoder dengan monitor
            monitor = MultipartEncoderMonitor(encoder, upload_callback)
            
            # Siapkan header content-type
            headers = {'Content-Type': monitor.content_type}

            # 4. Kirim request POST dengan 'data=monitor'
            response = requests.post(full_url, data=monitor, headers=headers)

        # 5. Tutup progress bar
        progress_bar.close()
        
        # --- AKHIR LOGIKA PROGRESS BAR ---

        if response.status_code == 200:
            try:
                data = response.json()
                video_id = data['id']
                cdn_link = f"https://cdn.videy.co/{video_id}.mp4"
                if not quiet: # Log ini tetap menghormati mode hening
                    print(f"  Upload SUKSES. Link CDN: {cdn_link}")
                return cdn_link
            except (ValueError, KeyError):
                if not quiet:
                    print("  Uploader ERROR PARSING: Upload sukses tapi format respons tidak valid.")
                return None
        else:
            if not quiet:
                print(f"  UPLOAD GAGAL: Server merespons dengan kode {response.status_code}.")
            return None

    except Exception as e:
        if not quiet:
            print(f"  KONEKSI GAGAL: {e}")
        if 'progress_bar' in locals():
            progress_bar.close()
        return None
