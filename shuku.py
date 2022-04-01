import requests
from bs4 import BeautifulSoup
import os
import re
from multiprocessing import Process, Queue, cpu_count


if os.name == 'nt':
    illegal_chars = r"[<>?/\\|:*\"]"
    root_path = 'C:\\Users\\15120\\Desktop\\crawler\\shuku'
elif os.name == 'posix':
    illegal_chars = r"[/]"
    root_path = '/home/data/zhangzhenhao-21/crawlers/guoxuemi/shuku'
else:
    raise ValueError("Unknown OS {}".format(os.name))

root_url = 'http://www.guoxuemi.com'

DONE_MSG = 'DONE'

def string_to_legal_filename(name):
    return re.sub(illegal_chars, "", name)


def error(msg):
    print(msg)
    exit()


def url2soup(url, max_retry=5):
    for _ in range(max_retry):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                error("Bad status code {} when crawling {}".format(response.status_code, url))
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, features="html.parser")
            return soup
        except:
            pass
    error("Failed to fetch {}".format(url))


def get_class_links(url):
    return [
        (string_to_legal_filename(tag.b.a.text), tag.b.a.get('href')) 
        for tag in url2soup(url).find_all('div', class_='xgwz2')
    ]


def get_subclass_links(url):
    return [
        (string_to_legal_filename(tag.b.a.text), tag.b.a.get('href')) 
        for tag in url2soup(url).find_all('section', class_='xgwz2')
    ]


def get_book_links(url):
    soup = url2soup(url)
    ul = soup.find('ul', class_='entry-related cols-3 post-loop post-loop-list')
    lis = ul.find_all('li', class_='item')
    name_dict, links = {}, []
    for tag in lis:
        # Filter out illegal chars for a filename
        name = string_to_legal_filename(tag.a.text)
        # Different books may have the same name
        if name in name_dict:
            name_dict[name] += 1
            name += str(name_dict[name])
        else:
            name_dict[name] = 0
        links.append((name, tag.a.get('href')))
    return links
get_chapter_links = get_book_links # same sturcture, share code


def get_and_save_chapter_text(url, path):
    soup = url2soup(url)
    content = soup.find('div', class_='entry-content clearfix')
    text = ''.join([child.text for child in content.children][2:])
    with open(path, "w", encoding='utf8') as fp:
        fp.writelines(text)


def worker(qin, qout):
    pid = os.getpid()
    while True:
        inst = qin.get()
        if len(inst) == 3:
            get_and_save_chapter_text(*(inst[:2]))
            qout.put("Process pid {} finished {}.".format(pid, inst[2]))
        elif inst == DONE_MSG:
            exit(0)
        else:
            raise ValueError("Unknown instruction.")


def printer(q):
    while True:
        inst = q.get()
        print(inst)
        if inst == DONE_MSG:
            exit(0)


def fireup_workers(n_workers=cpu_count()):
    qin, qout = Queue(), Queue()
    worker_processes = []
    for _ in range(n_workers):
        p = Process(target=worker, args=(qin, qout))
        p.start()
        worker_processes.append(p)
    printer_process = Process(target=printer, args=(qout,))
    printer_process.start()
    return qin, qout, worker_processes, printer_process


def cleanup_workers(qin, qout, worker_processes, printer_process):
    for _ in range(len(worker_processes)):
        qin.put(DONE_MSG)
    for wp in worker_processes:
        wp.join()
    qout.put(DONE_MSG)
    printer_process.join()
    print("Done!")


def clear(root_dir):
    for book in os.listdir(root_dir):
        book = os.path.join(root_dir, book)
        chapters=  os.listdir(book)
        for chapter in chapters:
            chapter = os.path.join(book, chapter)
            if not os.path.isdir(chapter):
                continue
            content = os.listdir(chapter)
            if len(content)==1 and content[0] == 'DONE.sym':
                print("Removing fake finished {}".format(chapter))
                shutil.rmtree(chapter)
        if len(os.listdir(book)) == 0:
            print("Removing empty book {}".format(book))
            shutil.rmtree(book)


def main():
    qin, qout, worker_processes, printer_process = fireup_workers()

    class_links = get_class_links(root_url + '/shuku')
    for class_name, class_link in class_links:
        subclass_links = get_subclass_links(root_url + class_link)
        for subclass_name, subclass_link in subclass_links:
            book_links = get_book_links(root_url + subclass_link)
            for book_name, book_link in book_links:
                chapter_links = get_chapter_links(root_url + book_link)

                book_path = os.path.join(root_path, class_name, subclass_name, book_name)
                if not os.path.exists(book_path):
                    os.makedirs(book_path)
                elif len(chapter_links) == len(os.listdir(book_path)):
                    qout.put("Already got book {} of class {}, pass.".format(book_name, class_name))
                    continue
                
                for chapter_name, chapter_link in chapter_links:
                    chapter_path = os.path.join(book_path, chapter_name+'.txt')
                    chapter_url = root_url + chapter_link
                    if not os.path.exists(chapter_path):
                        qin.put((chapter_url, chapter_path, book_name+'-'+chapter_name))
                    else:
                        qout.put("Already got chapter {} of book {}, pass.".format(chapter_name, book_name))

    cleanup_workers(qin, qout, worker_processes, printer_process)


if __name__ == '__main__':
    main()