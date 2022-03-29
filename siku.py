import requests
from bs4 import BeautifulSoup
import os
import re
import shutil


# The chapter names and books name may contain illegal chars
# for a windows file name.
illegal_chars = r"[<>?/\\|:*\"]"
def string_to_legal_windows_file_name(name):
    return re.sub(illegal_chars, "", name)


def error(msg):
    print(msg)
    exit()


def url2soup(url):
    response = requests.get(url)
    if response.status_code != 200:
        error("Bad status code {} when crawling {}".format(response.status_code, url))
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, features="html.parser")
    return soup


def craw_book_links(root_url):
    soup = url2soup(root_url)
    articles = soup.find('article', id='post-24142')

    name_dict = dict() # In case of different books with the same name.
    links = []
    for link in articles.find_all('a'):
        name = string_to_legal_windows_file_name(link.text)
        if name in name_dict:
            name_dict[name] += 1
            name += str(name_dict[name])
        else:
            name_dict[name] = 0
        links.append((name, link.get('href')))
    return links


def crawl_book(book_url):
    soup = url2soup(book_url)
    ul = soup.find('ul', class_='entry-related cols-3 post-loop post-loop-list')

    name_dict = dict() # In case of different chapters with the same name.
    links = []
    for link in ul.find_all('a'):
        name = string_to_legal_windows_file_name(link.text)
        if name in name_dict:
            name_dict[name] += 1
            name += str(name_dict[name])
        else:
            name_dict[name] = 0
        links.append((name, link.get('href')))
    return links


def crawl_chapter(chap_url):
    soup = url2soup(chap_url)
    content = soup.find('div', class_='entry-content clearfix')
    text = [child.text for child in content.children][2:]
    return ''.join(text)


def download_books(domain, book_links, local_path):
    print("Books will be saved in {}".format(local_path))

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    for book_name, book_link in book_links:

        book_url = domain + book_link
        chapters = crawl_book(book_url)

        book_path = os.path.join(local_path, book_name)
        if not os.path.exists(book_path):
            os.makedirs(book_path)
        elif len(os.listdir(book_path)) == len(chapters):
            # Skip the downloaded books
            print("Already downloaded {}, pass.".format(book_name))
            continue
        elif len(os.listdir(book_path)) > len(chapters):
            # Redownloaed the problematic books
            shutil.rmtree(book_path)
            os.makedirs(book_path)
        
        for chap_name, chap_link in chapters:
            chap_path = os.path.join(book_path, chap_name+'.txt')
            if os.path.exists(chap_path):
                # Skip the downloaded chapters.
                print("Already downloaded chapter {} of book {}, pass.".format(chap_name, book_name))
                continue
            text = crawl_chapter(domain + chap_link)
            with open(chap_path, "w", encoding='utf8') as f:
                f.writelines(text)
        print("Finished book:", book_name)



def main():
    root_url = 'http://www.guoxuemi.com/SiKuQuanShu'
    book_links = craw_book_links(root_url)
    download_books('http://www.guoxuemi.com', book_links, "C:/Users/15120/Desktop/crawler/SiKuQuanShu")
    print("Done")
    

if __name__ == '__main__':
    main()