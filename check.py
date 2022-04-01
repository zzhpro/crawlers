import os


def check(gjzx_path):
    full_chap_cnt, img_cnt = 0, 0
    for book in os.listdir(gjzx_path):
        book_path = os.path.join(gjzx_path, book)
        for chap in os.listdir(book_path):
            chap_path = os.path.join(book_path, chap)
            if not os.path.isdir(chap_path):
                continue
            content = os.listdir(chap_path)
            if "DONE.sym" in content and len(content) > 1:
                full_chap_cnt += 1
                img_cnt += len(content) - 1
    print(f"Got {full_chap_cnt} full chapters, {img_cnt} images.")


if __name__ == '__main__':
    check("/home/data/zhangzhenhao-21/crawlers/guoxuemi/gjzx")