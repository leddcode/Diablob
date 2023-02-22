import os
from threading import Lock, Thread
import time

from bs4 import BeautifulSoup as bs       
import colorama
from colorama import Fore, Style
import requests

colorama.init()


class AzureContainer:
    LOCK = Lock()

    def __init__(self, container_url):
        self.base = container_url + '?restype=container&comp=list&marker='
        self.directory = self.create_output_directory()

    def create_output_directory(self):
        directory = f'results/blobs{int(time.time())}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def get_soup(self, url):
        return bs(requests.get(url).content, 'xml')

    def write_current_page_data(self, page_number=1, marker=''):
        url = self.base + marker
        self.LOCK.acquire()
        print(f'{Fore.GREEN}[+] Parsing{Style.RESET_ALL} {url} {Fore.GREEN}(page {page_number}){Style.RESET_ALL}')
        self.LOCK.release()
        soup = self.get_soup(url)
        next_marker = soup.find('NextMarker')
        if next_marker.text:
            Thread(target=self.write_current_page_data, args=(page_number + 1, next_marker.text)).start()
        title = f'SOURCE: {url}'
        delimiter = '-' * len(title)
        with open(f'{self.directory}/blobs_{page_number}.txt', 'w+', encoding='utf-8', errors='ignore') as f:
            f.write(f'{title}\n{delimiter}\n\n')
            for url in soup.find_all('Url'):
                f.write(f'{url.text}\n')


if __name__ == "__main__":
    print(f'''{Fore.RED}
     __          __        __   __  
    |  \ |  /\  |__) |    /  \ |__) {Style.RESET_ALL}v1.0.0{Fore.RED}
    |__/ | /~~\ |__) |___ \__/ |__) {Style.RESET_ALL}by @leddcode{Fore.YELLOW}
    ''')

    container_url = input('[?] Enter Azure Blob Container URL: ')
    try:
        AzureContainer(container_url).write_current_page_data()
    except Exception:
        print(f'{Fore.RED}[!] Oops.. Something went wrong - check the container url and try again!{Style.RESET_ALL}')
