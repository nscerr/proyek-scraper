# uploader.py

import requests
import os
import uuid
import mimetypes

# --- Konfigurasi ---
MAX_SIZE_MB = 100
URL_ENDPOINT = "https://videy.co/api/upload"

def upload(local_file_path):
    """
    Meng-upload satu file video ke videy.co dan mengembalikan URL CDN.
    Mengembalikan None jika gagal.
    """
    
    # --- 1. BLOK VALIDASI ---
    # Periksa apakah file ada
    if not os.path.exists(local_file_path):
        print(f"Uploader ERROR: File '{local_file_path}' tidak ditemukan.")
        return None # Gagal
    
    # Periksa ukuran file
    file_size_bytes = os.path.getsize(local_file_path)
    max_size_bytes = MAX_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        print(f"Uploader ERROR: Ukuran file ({file_size_bytes / 1024 / 1024:.2f} MB) melebihi batas ({MAX_SIZE_MB} MB).")
        return None # Gagal

    # --- 2. Proses Upload (jika validasi lolos) ---
    visitor_id = str(uuid.uuid4())
    full_url = f"{URL_ENDPOINT}?visitorId={visitor_id}"
    
    # Logging untuk memberi tahu user apa yang terjadi
    print(f"  Uploading '{os.path.basename(local_file_path)}' ke Videy.co...")

    try:
        with open(local_file_path, 'rb') as f:
            mime_type, _ = mimetypes.guess_type(local_file_path)
            if mime_type is None: mime_type = 'application/octet-stream'

            files_payload = {
                'file': (os.path.basename(local_file_path), f, mime_type)
            }

            response = requests.post(full_url, files=files_payload)

            if response.status_code == 200:
                try:
                    data = response.json()
                    video_id = data['id']
                    cdn_link = f"https://cdn.videy.co/{video_id}.mp4"
                    print(f"  Upload SUKSES. Link CDN: {cdn_link}")
                    return cdn_link # Berhasil!
                except (ValueError, KeyError):
                    print("  Uploader ERROR PARSING: Upload sukses tapi format respons tidak valid.")
                    return None # Gagal
            else:
                print(f"  UPLOAD GAGAL: Server merespons dengan kode {response.status_code}.")
                return None # Gagal

    except requests.exceptions.RequestException as e:
        print(f"  KONEKSI GAGAL: {e}")
        return None # Gagal
