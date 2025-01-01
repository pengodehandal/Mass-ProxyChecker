import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from termcolor import colored
import sys
import time
import signal

ASCII_ART = """
██████╗ ██╗     ███╗   ███╗ ██████╗ ███████╗███████╗██╗  ██╗███████╗████████╗
██╔══██╗██║     ████╗ ████║██╔══██╗██╔════╝██╔════╝██║  ██║██╔════╝╚══██╔══╝
██████╔╝██║     ██╔████╔██║██████╔╝███████╗█████╗  ███████║███████╗   ██║
██╔═══╝ ██║     ██║╚██╔╝██║██╔══██╗╚════██║██╔══╝  ██╔══██║╚════██║   ██║
██║     ███████╗██║ ╚═╝ ██║██████╔╝███████║███████╗██║  ██║███████╗   ██║
╚═╝     ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝
                                                                              
            GitHub: https://github.com/pengodehandal/Mass-ProxyChecker
"""

running = True

def check_proxy(proxy, url, protocol, proxy_type):
    try:
        proxies = {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }
        response = requests.get(url, proxies=proxies, timeout=4)
        if response.status_code == 200:
            success_message = f"Berhasil Mengakses {url} Status Proxy: {protocol} IP:PORT: {proxy} Status Code: {response.status_code}"
            print(colored(success_message, 'green'))

            if protocol == 'HTTP':
                with open('ProxyHttp.txt', 'a') as file:
                    file.write(proxy + '\n')
            elif protocol == 'HTTPS':
                with open('ProxyHttps.txt', 'a') as file:
                    file.write(proxy + '\n')

        else:
            print(colored(f"Proxy {proxy} gagal dengan status code: {response.status_code}", 'red'))

    except requests.exceptions.Timeout:
        print(colored(f"Proxy {proxy} tidak bisa connect. Timeout setelah 4 detik.", 'red'))

    except requests.exceptions.ProxyError:
        print(colored(f"Proxy {proxy} tidak bisa connect. Proxy error.", 'red'))

    except requests.RequestException as e:
        print(colored(f"Proxy {proxy} gagal. Error: {str(e)}", 'red'))

def get_proxy_list(input_file):
    proxy_list = []
    try:
        with open(input_file, 'r') as f:
            proxy_list = [line.strip() for line in f.readlines() if line.strip()]
        proxy_list = list(set(proxy_list))
    except Exception as e:
        print(f"Error reading proxy list file: {e}")
    return proxy_list

def signal_handler(sig, frame):
    global running
    print("\nMenghentikan program...")
    running = False
    sys.exit(0)

def loading_animation():
    loading_text = "Loading"
    for i in range(5):
        print(f"\r{loading_text}{'.' * (i % 4)}", end="")
        time.sleep(0.5)
    print("\r", end="")

def main():
    print(colored(ASCII_ART, 'cyan'))
    loading_animation()
    signal.signal(signal.SIGINT, signal_handler)

    url_http = "http://httpstat.us/"
    url_https = "https://httpstat.us/200"

    proxy_file = input("Masukkan file yang berisi daftar proxy (contoh: proxies.txt): ")
    thread_count = int(input("Masukkan jumlah thread yang ingin digunakan untuk pengecekan (misal: 5): "))

    proxy_list = get_proxy_list(proxy_file)
    
    if len(proxy_list) == 0:
        print("Daftar proxy kosong atau file tidak ditemukan.")
        sys.exit(1)

    print("\nPilih jenis proxy yang ingin diperiksa:")
    print("1. HTTP Proxy")
    print("2. HTTPS Proxy")
    proxy_choice = input("Masukkan pilihan (1 atau 2): ").strip()

    if proxy_choice == '1':
        print("\nMengecek HTTP proxies...")
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures_http = [executor.submit(check_proxy, proxy, url_http, "HTTP", 'http') for proxy in proxy_list]
            for future in futures_http:
                try:
                    future.result()
                except TimeoutError:
                    print(f"Timeout saat memeriksa proxy {future.arg[0]}")
                except Exception as e:
                    print(f"Error occurred while checking proxy: {str(e)}")

    elif proxy_choice == '2':
        print("\nMengecek HTTPS proxies...")
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures_https = [executor.submit(check_proxy, proxy, url_https, "HTTPS", 'https') for proxy in proxy_list]
            for future in futures_https:
                try:
                    future.result()
                except TimeoutError:
                    print(f"Timeout saat memeriksa proxy {future.arg[0]}")
                except Exception as e:
                    print(f"Error occurred while checking proxy: {str(e)}")
    else:
        print("Pilihan tidak valid. Silakan pilih 1 untuk HTTP atau 2 untuk HTTPS.")
        sys.exit(1)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\nPengecekan selesai. Waktu yang dibutuhkan: {end_time - start_time:.2f} detik.")
