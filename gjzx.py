import datetime
import requests
import logging
from bs4 import BeautifulSoup
import os
import re
from multiprocessing import Process, Queue, cpu_count
import signal
import shutil

# TODO: 用logging管理输出，同时输出至日志文件和标准输出
# TODO: 加入sanity check DONE
# TODO: 修复printer无法正确退出的bug DONE

if os.name == 'nt':
    illegal_chars = r"[<>?/\\|:*\"]"
    root_path = 'C:\\Users\\15120\\Desktop\\crawler\\test'
    log_path = 'C:\\Users\\15120\\Desktop\\crawler\\log'
elif os.name == 'posix':
    illegal_chars = r"[/]"
    root_path = '/home/data/zhangzhenhao-21/crawlers/guoxuemi/gjzx'
    log_path = '/home/data/zhangzhenhao-21/crawlers/log'
else:
    raise ValueError("Unknown OS {}".format(os.name))

root_url = 'http://www.guoxuemi.com'
DONE_MSG = 'DONE'
DONE_FILENAME = 'DONE.sym'


def clear_files():
    for book in os.listdir(root_path):
        book = os.path.join(root_path, book)
        chapters = os.listdir(book)
        for chapter in chapters:
            chapter = os.path.join(book, chapter)
            if not os.path.isdir(chapter):
                continue
            content = os.listdir(chapter)
            if len(content) == 0 or content == ['DONE.sym']:
                print("Removing fake finished {}".format(chapter))
                shutil.rmtree(chapter)
        valid_chs = os.listdir(book)
        if len(valid_chs) == 0 or valid_chs == ['intro.txt']:
            print("Removing empty book {}".format(book))
            shutil.rmtree(book)


class MPManager:
    def __init__(self, n_workers=cpu_count()):
        qin, qout = Queue(), Queue()
        worker_procs = []
        for _ in range(n_workers):
            p = Process(target=worker, args=(qin, qout))
            p.start()
            worker_procs.append(p)
        printer_proc = Process(target=printer, args=(qin, qout))
        printer_proc.start()

        self.n_workers = n_workers
        self.worker_procs = worker_procs
        self.printer_proc = printer_proc
        self.qin, self.qout = qin, qout

        def clear(sig, frame):
            all_procs = self.worker_procs + [printer_proc]
            for p in all_procs:
                try:
                    os.kill(p.pid, signal.SIGINT)
                except:
                    pass
            for p in all_procs:
                p.join()
            print("Done cleaning up procs.")
            clear_files()
            print("Done cleaning up files.")
            print("Done.")
            os._exit(-1)

        signal.signal(signal.SIGINT, clear)
    
    def cleanup_workers(self):
        for _ in range(len(self.worker_procs)):
            self.qin.put(DONE_MSG)
        for wp in self.worker_procs:
            wp.join()
        self.qout.put(DONE_MSG)
        self.printer_proc.join()
        print("Done cleaning up workers!")
        

def string_to_legal_filename(name):
    return re.sub(illegal_chars, "", name)


def error(msg):
    print(msg)
    os._exit(-1)


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


def get_book_links(url):
    soup = url2soup(url)
    section = soup.find('section', class_='xgwz2')
    lis = section.find_all('li')
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


def get_chapter_links(url):
    soup = url2soup(url)
    ul = soup.find('section', class_='xgwz2').ul
    lis = ul.find_all('li')
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


def get_intro_chapter_links(url):
    soup = url2soup(url)
    # Get the introduction of the book
    intro_tag = soup.find('div', class_='entry-content clearfix')
    intro = ''.join(child.text for child in intro_tag.children)
    links = get_chapter_links(url)
    return intro, links


def get_and_save_chapter_images(chapter_url,  path, max_retry=5):
    soup = url2soup(chapter_url)
    code = soup.find('section', class_='xgwz2').find_all('script')[-1].text

    prefix_re = r"var ml='([a-z0-9:/\.]*)';"
    filenames_re = r"imglist\[\d+\]='(\d+\.\w+)';"
    prefix = re.search(prefix_re, code).group(1)
    file_lt = re.findall(filenames_re, code)

    if len(file_lt) == 0:
        with open(os.path.join(log_path, "strange.txt"), "a+") as fp:
            fp.write(chapter_url+'\n')
        return "all"
    else:
        bad_count = 0
        for filename in file_lt:
            full_path = os.path.join(path, filename)
            if not os.path.exists(full_path):
                for retry in range(max_retry):
                    try:
                        r = requests.get(prefix + filename)
                        if r.status_code != 200:
                            continue
                        with open(full_path, "wb") as fp:
                            fp.write(r.content)
                        break
                    except:
                        pass
                    if retry == max_retry - 1:
                        bad_count += 1
                
        # Leave a symbol file to mark the completeness of a chapter
        if bad_count == 0:
            with open(os.path.join(path, DONE_FILENAME), 'w') as fp:
                fp.write('')
        return bad_count


def int_handler(sig, frame):
    os._exit(-1)


def worker(qin, qout):
    signal.signal(signal.SIGINT, int_handler)
    pid = os.getpid()
    while True:
        inst = qin.get()
        if len(inst) == 3:
            bad_count = get_and_save_chapter_images(*(inst[:-1]))
            if bad_count != 0:
                qout.put("Process {} failed to get {} pics of {}".format(pid, bad_count, inst[-1]))
            else:
                qout.put("Process {} finished {}, {} jobs remain, at {}".format(
                    pid, inst[-1], qin.qsize(), datetime.datetime.now()))
        elif inst == DONE_MSG:
            qout.put("Process {} is exiting.".format(pid))
            qout.close()
            qout.join_thread()
            break
        else:
            qout.put("Process {} died from wired instruction.".format(pid))
            qout.close()
            qout.join_thread()
            raise ValueError("Unknown instruction.")


def printer(qin, qout):
    log_file = os.path.join(log_path, str(datetime.datetime.now())+"_gjzx.log")
    logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)
    signal.signal(signal.SIGINT, int_handler)
    while True:
        inst = qout.get()
        logging.info(inst)
        if inst == DONE_MSG:
            break


def main(n_repeat, n_workers):
    manager = MPManager(n_workers=n_workers)
    
    for _ in range(n_repeat):
        book_links = get_book_links(root_url + '/gjzx')
        for book_name, book_link in book_links:
            intro_text, chapter_links = get_intro_chapter_links(root_url + book_link)
            intro_text = intro_text.strip()

            book_path = os.path.join(root_path, book_name)
            if not os.path.exists(book_path):
                os.makedirs(book_path)

            if len(intro_text) > 0:
                with open(os.path.join(book_path, 'intro.txt'), 'w', encoding='utf8') as fp:
                    fp.writelines(intro_text)
            
            for chapter_name, chapter_link in chapter_links:
                chapter_path = os.path.join(book_path, chapter_name)
                if not os.path.exists(chapter_path):
                    os.makedirs(chapter_path)
                elif os.path.exists(os.path.join(chapter_path, DONE_FILENAME)):
                    manager.qout.put("Already got chapter {} of {}, pass.".format(chapter_name, book_name))
                    continue
                
                chapter_url = root_url + chapter_link
                manager.qin.put((chapter_url, chapter_path, book_name+'-'+chapter_name))

    manager.cleanup_workers()
    clear_files()
    print("Done.")


if __name__ == '__main__':
    main(n_repeat=1, n_workers=3)
