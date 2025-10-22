import sys
import argparse
import json
from urllib.parse import urlparse

# Impor setiap fungsi 'scrape' dari file kita
from scrapers.kaotic_scraper import scrape as scrape_kaotic
from scrapers.seegore_scraper import scrape as scrape_seegore
from scrapers.gorecenter_scraper import scrape as scrape_gorecenter
from scrapers.xgore_scraper import scrape as scrape_xgore
from scrapers.bestgore_scraper import scrape as scrape_bestgore

def main():
    # 1. Siapkan parser argumen
    parser = argparse.ArgumentParser(description="Scraper Video Multi-Situs.")
    parser.add_argument("-u", "--url", required=True, help="URL postingan yang ingin di-scrape.")
    args = parser.parse_args()
    
    url_postingan = args.url
    
    # 2. Dapatkan domain dari URL untuk 'dispatcher'
    try:
        # urlparse('https://seegore.com/abc').netloc -> 'seegore.com'
        domain = urlparse(url_postingan).netloc
    except Exception as e:
        print(json.dumps({"error": f"URL tidak valid: {e}"}, indent=2))
        sys.exit(1)

    # 3. Logika Dispatcher (Si Manajer)
    # Memilih "pekerja" (scraper) yang tepat
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

    # 4. Tampilkan Hasil Akhir
    # Ini adalah SATU-SATUNYA 'print' yang dilihat pengguna.
    # json.dumps mengubah dictionary Python menjadi teks JSON yang rapi.
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()

print("Semua file telah dibuat: main.py dan 5 file di dalam folder scrapers/")
