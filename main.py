# main.py (VERSI BARU)

import sys
import argparse
import json
import os
from urllib.parse import urlparse

# ----------------------------------------------------
# Impor baru untuk alur kerja lengkap
# ----------------------------------------------------
import downloader
import uploader
from scrapers.kaotic_scraper import scrape as scrape_kaotic
from scrapers.seegore_scraper import scrape as scrape_seegore
from scrapers.gorecenter_scraper import scrape as scrape_gorecenter
from scrapers.xgore_scraper import scrape as scrape_xgore
from scrapers.bestgore_scraper import scrape as scrape_bestgore
# ----------------------------------------------------

# Tentukan folder temp di Colab (di luar folder git)
TEMP_FOLDER = "/content/temp_video_downloads"


def main():
    parser = argparse.ArgumentParser(description="Alur Kerja Scraper & Uploader Video Multi-Situs.")
    parser.add_argument("-u", "--url", required=True, help="URL postingan yang ingin diproses.")
    args = parser.parse_args()
    
    url_postingan = args.url
    
    try:
        domain = urlparse(url_postingan).netloc
        # Buat URL referer dasar (misal: https://xgore.net/)
        referer_url = f"{urlparse(url_postingan).scheme}://{domain}/"
    except Exception as e:
        print(json.dumps({"error": f"URL tidak valid: {e}"}, indent=2))
        sys.exit(1)

    # ----------------------------------------------------
    # LANGKAH 1: SCRAPE (Mendapatkan Data)
    # ----------------------------------------------------
    print(f"Memulai LANGKAH 1: SCRAPE data dari {domain}...")
    data = {}
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

    # Periksa apakah scraper gagal
    if data.get("error"):
        print(json.dumps(data, indent=2))
        sys.exit(1)

    video_urls_sumber = data.get("video_urls", [])
    if not video_urls_sumber or "Tidak Ditemukan" in video_urls_sumber[0]:
        print(json.dumps({"error": "Scraper berhasil, tapi tidak ada URL video yang ditemukan.", "data": data}, indent=2))
        sys.exit(1)
        
    print(f"Scrape SUKSES. Ditemukan {len(video_urls_sumber)} video.")

    # ----------------------------------------------------
    # LANGKAH 2 & 3: DOWNLOAD -> UPLOAD (Looping)
    # ----------------------------------------------------
    cdn_links_final = []
    
    for i, video_url in enumerate(video_urls_sumber, 1):
        print(f"\n--- Memproses Video {i} dari {len(video_urls_sumber)}: {video_url} ---")
        
        # Tentukan referer (hanya untuk xgore.net)
        referer_untuk_download = None
        if data.get("situs") == "xgore":
            referer_untuk_download = referer_url

        # LANGKAH 2: DOWNLOAD
        local_file_path = downloader.download_video(video_url, TEMP_FOLDER, referer=referer_untuk_download)
        
        if local_file_path:
            # LANGKAH 3: UPLOAD
            cdn_url = uploader.upload(local_file_path)
            
            if cdn_url:
                cdn_links_final.append(cdn_url)
            else:
                cdn_links_final.append(f"UPLOAD GAGAL untuk: {video_url}")
            
            # LANGKAH 4: CLEAN UP (Hapus file temp)
            try:
                os.remove(local_file_path)
                print(f"  File temp '{local_file_path}' berhasil dihapus.")
            except OSError as e:
                print(f"  PERINGATAN: Gagal menghapus file temp '{local_file_path}'. Error: {e}")
        
        else:
            cdn_links_final.append(f"DOWNLOAD GAGAL untuk: {video_url}")
            
    # ----------------------------------------------------
    # LANGKAH 5: TAMPILKAN HASIL AKHIR
    # ----------------------------------------------------
    
    # Kumpulkan semua data untuk output JSON akhir
    hasil_akhir = {
        "situs_asal": data.get("situs", "Tidak diketahui"),
        "judul_asal": data.get("judul", "Tidak diketahui"),
        "url_sumber_postingan": url_postingan,
        "jumlah_video_diproses": len(video_urls_sumber),
        "url_cdn_hasil": cdn_links_final,
        "data_scraper_lengkap": data # Selipkan semua data asli
    }
    
    print("\n" + "="*40)
    print("      PROSES SELESAI      ")
    print("="*40)
    # Cetak JSON akhir yang rapi
    print(json.dumps(hasil_akhir, indent=2))

if __name__ == "__main__":
    main()
