# main.py (VERSI BARU DENGAN FFMPEG FIX)

import sys
import argparse
import json
import os
import subprocess # <- IMPOR BARU
import shutil     # <- IMPOR BARU
from urllib.parse import urlparse

import downloader
import uploader
from scrapers.kaotic_scraper import scrape as scrape_kaotic
from scrapers.seegore_scraper import scrape as scrape_seegore
from scrapers.gorecenter_scraper import scrape as scrape_gorecenter
from scrapers.xgore_scraper import scrape as scrape_xgore
from scrapers.bestgore_scraper import scrape as scrape_bestgore

TEMP_FOLDER = "/content/temp_video_downloads"

def main():
    parser = argparse.ArgumentParser(description="Alur Kerja Scraper & Uploader Video Multi-Situs.")
    parser.add_argument("-u", "--url", required=True, help="URL postingan yang ingin diproses.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Mode hening, sembunyikan log proses dan hanya tampilkan JSON akhir.")
    args = parser.parse_args()
    
    url_postingan = args.url
    is_quiet = args.quiet
    
    # Cek apakah ffmpeg ada
    if shutil.which("ffmpeg") is None:
        print(json.dumps({"error": "FATAL: ffmpeg tidak ditemukan. Proses dibatalkan."}, indent=2))
        sys.exit(1)
        
    try:
        domain = urlparse(url_postingan).netloc
        referer_url = f"{urlparse(url_postingan).scheme}://{domain}/"
    except Exception as e:
        print(json.dumps({"error": f"URL tidak valid: {e}"}, indent=2))
        sys.exit(1)

    # ----------------------------------------------------
    # LANGKAH 1: SCRAPE
    # ----------------------------------------------------
    if not is_quiet:
        print(f"Memulai LANGKAH 1: SCRAPE data dari {domain}...")
        
    data = {}
    # (Logika if/elif untuk memilih scraper... tetap sama)
    if 'kaotic.com' in domain:
        data = scrape_kaotic(url_postingan)
    elif 'seegore.com' in domain:
        data = scrape_seegore(url_postingan)
    elif 'gorecenter.com' in domain:
        data = scrape_gorecenter(url_postingan)
    elif 'xgore.net' in domain:
        data = scrape_xgore(url_postingan)
    elif 'bestgore.fun' in domain:
        data = scrape_bestgore(url_postingan)
    else:
        data = {"error": f"Tidak ada scraper yang dikonfigurasi untuk domain: {domain}"}

    if data.get("error"):
        print(json.dumps(data, indent=2))
        sys.exit(1)

    video_urls_sumber = data.get("video_urls", [])
    if not video_urls_sumber or "Tidak Ditemukan" in video_urls_sumber[0]:
        data["error"] = "Scraper berhasil, tapi tidak ada URL video yang ditemukan."
        print(json.dumps(data, indent=2))
        sys.exit(1)
        
    if not is_quiet:
        print(f"Scrape SUKSES. Ditemukan {len(video_urls_sumber)} video.")

    # ----------------------------------------------------
    # LANGKAH 2, 3, 4: DOWNLOAD -> FIX -> UPLOAD -> CLEANUP
    # ----------------------------------------------------
    processed_video_urls = [] 
    
    for i, video_url in enumerate(video_urls_sumber, 1):
        if not is_quiet:
            print(f"\n--- Memproses Video {i} dari {len(video_urls_sumber)}: {video_url} ---")
        
        referer_untuk_download = None
        if data.get("source_site") == "xgore":
            referer_untuk_download = referer_url

        # LANGKAH 2: DOWNLOAD
        local_file_path = downloader.download_video(video_url, TEMP_FOLDER, referer=referer_untuk_download, quiet=is_quiet)
        
        if local_file_path:
            
            # --- LANGKAH 2.5: FFMPEG FIX (BARU!) ---
            upload_file_path = local_file_path # Default, gunakan file asli
            fixed_file_path = None # Path untuk file yg di-fix
            
            # Cek jika ini dari bestgore, maka kita FIX
            if data.get("source_site") == "bestgore":
                if not is_quiet:
                    print(f"  -> Sumber 'bestgore', menjalankan FFMPEG remux (fast-start)...")
                
                # Buat nama file baru (misal: abcde_fixed.mp4)
                path_tanpa_ekstensi, ekstensi = os.path.splitext(local_file_path)
                fixed_file_path = f"{path_tanpa_ekstensi}_fixed{ekstensi}"
                
                # Perintah FFMPEG
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-i", local_file_path,
                    "-c", "copy",
                    "-movflags", "+faststart",
                    fixed_file_path,
                    "-loglevel", "error" # Sembunyikan log ffmpeg
                ]
                
                try:
                    subprocess.run(ffmpeg_cmd, check=True)
                    # SUKSES! Gunakan file yang sudah di-fix untuk di-upload
                    upload_file_path = fixed_file_path 
                    if not is_quiet:
                        print(f"  -> Remux SUKSES. File baru: {fixed_file_path}")
                except subprocess.CalledProcessError as e:
                    if not is_quiet:
                        print(f"  -> PERINGATAN: FFMPEG remux GAGAL. Tetap meng-upload file asli.")
                    # Jika remux gagal, kita tetap coba upload file aslinya
                    upload_file_path = local_file_path
            
            # --- AKHIR DARI FFMPEG FIX ---
            
            # LANGKAH 3: UPLOAD
            cdn_url = uploader.upload(upload_file_path, quiet=is_quiet)
            
            if cdn_url:
                processed_video_urls.append(cdn_url)
            else:
                processed_video_urls.append(video_url) 
            
            # LANGKAH 4: CLEAN UP
            try:
                os.remove(local_file_path) # Hapus file download asli
                if fixed_file_path and os.path.exists(fixed_file_path):
                    os.remove(fixed_file_path) # Hapus juga file yg di-fix
                
                if not is_quiet:
                    print(f"  File temp berhasil dihapus.")
            except OSError as e:
                if not is_quiet:
                    print(f"  PERINGATAN: Gagal menghapus file temp. Error: {e}")
        
        else:
            processed_video_urls.append(video_url)
            
    # ----------------------------------------------------
    # LANGKAH 5: TAMPILKAN HASIL AKHIR
    # ----------------------------------------------------
    
    data['video_urls'] = processed_video_urls
    data['source_post_url'] = url_postingan

    if not is_quiet:
        print("\n" + "="*40)
        print("      PROSES SELESAI      ")
        print("="*40)
    
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
