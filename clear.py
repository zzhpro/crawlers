import os
import shutil

def clear(root_dir):
    for book in os.listdir(root_dir):
        book = os.path.join(root_dir, book)
        chapters=  os.listdir(book)
        for chapter in chapters:
            chapter = os.path.join(book, chapter)
            if not os.path.isdir(chapter):
                continue
            content = os.listdir(chapter)
            if len(content)==0 or (len(content)==1 and content[0] == 'DONE.sym'):
                print("Removing fake finished {}".format(chapter))
                shutil.rmtree(chapter)
                valid_chs = os.listdir(book)
        if len(valid_chs) == 0 or valid_chs==['intro.txt']:
            print("Removing empty book {}".format(book))
            shutil.rmtree(book)


clear('/home/data/zhangzhenhao-21/crawler/guoxuemi/gjzx')
