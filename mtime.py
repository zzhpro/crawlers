from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import json

DEBUG = 0

# fid fname
# aid aname
# fid aid * n
fid2fname, aid2aname, baskets = {}, {}, {}

def metric_func(xpath, plural):
    def gotit(driver):
        if plural:
            return driver.find_elements(By.XPATH, xpath)
        else:
            return driver.find_element(By.XPATH, xpath)
    return gotit


def crawl_actors(driver, fid ,max_actors):
    url = "http://movie.mtime.com/{}/fullcredits".format(fid)
    driver.get(url)
    actor_xpath = '//*[@id="app"]/div/div[3]/div[1]/div[@class="actorItem"]/div[1]/div/p[1]/a'
    wait = WebDriverWait(driver, 3)
    actor_list = wait.until(metric_func(actor_xpath, True))
    tlist = baskets[fid] = []
    for idx, actor in enumerate(actor_list):
        name = actor.text
        aid = int(actor.get_attribute("href").split('/')[-2])
        tlist.append(aid)
        aid2aname[aid] = name
        if idx == max_actors - 1:
            break


def crawl_movies(driver, n_pages):
    # Load root webpage
    root_url = 'http://film.mtime.com/search/movies/movies?more=true'    
    china_xpath = '//*[@id="app"]/div/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/ul/li[2]'
    driver.get(root_url)
    wait = WebDriverWait(driver, 5)
    # Find and click on the button "China"
    china_button = wait.until(metric_func(china_xpath, False))
    china_button.click()
    new_china_xpath = '//*[@id="app"]/div/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/span'
    wait.until(metric_func(new_china_xpath, False))
    
    for i in range(n_pages):
        # Load the movie list
        time.sleep(3)
        movie_xpath = '//*[@id="app"]/div/div[2]/div[3]/div/div[2]/div/div[3]/div[1]/ul/li'
        movie_list = wait.until(metric_func(movie_xpath, True))
        name_xpath = './h3/span[1]/span[1]'
        link_xpath = './div[last()]/div[last()]/div[last()]/a'
        for movie in movie_list:
            try:
                name = movie.find_element(By.XPATH, name_xpath).text
                link = movie.find_element(By.XPATH, link_xpath).get_attribute('href')
                fid = int(link.split('/')[-2])
                print(name, link, fid)
                fid2fname[fid] = name
            except NoSuchElementException:
                pass

        if i != n_pages - 1:
            next_xpath = '//*[@id="app"]/div/div[2]/div[3]/div/div[2]/div/div[3]/div[1]/ul/div/div/button[2]'
            next_button = driver.find_element(By.XPATH, next_xpath)
            next_button.click()


def main():
    options = Options()
    options.headless = not DEBUG
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)

    crawl_movies(driver, 30)
    for fid in fid2fname:
        try:
            crawl_actors(driver, fid, 20)
        except TimeoutException:
            print("Passed {} because of timeout.".format(fid2fname[fid]))
    
    # Save something
    with open("film.json", "w", encoding='utf8') as fp:
        json.dump(fid2fname, fp, ensure_ascii=False)
    with open("actor.json", "w", encoding='utf8') as fp:
        json.dump(aid2aname, fp, ensure_ascii=False)
    with open("basket.json", "w", encoding='utf8') as fp:
        json.dump(baskets, fp, ensure_ascii=False)

def json2strange():
    with open("film.json", "r", encoding='utf8') as fp:
        fid2fname = json.load(fp)
    with open("actor.json", "r", encoding='utf8') as fp:
        aid2aname = json.load(fp)
    with open("basket.json", "r", encoding='utf8') as fp:
        baskets = json.load(fp)
    with open("final.txt", "w", encoding='utf8') as fp:
        fp.write("people\n")
        for fid, aids in baskets.items():
            try:
                # row = [fid2fname[fid]] + [aid2aname[str(aid)] for aid in aids]
                row = [aid2aname[str(aid)] for aid in aids]
                row = list(filter(lambda x: x!='', row))
                fp.write('"' + ','.join(row) + '"\n')
            except KeyError:
                print("Key error")

def json2normal():
    with open("film.json", "r", encoding='utf8') as fp:
        fid2fname = json.load(fp)
    with open("actor.json", "r", encoding='utf8') as fp:
        aid2aname = json.load(fp)
    with open("basket.json", "r", encoding='utf8') as fp:
        baskets = json.load(fp)
    with open("final.txt", "w", encoding='utf8') as fp:
        for fid, aids in baskets.items():
            try:
                row = [fid2fname[fid]] + [aid2aname[str(aid)] for aid in aids]
                fp.write(','.join(row) + '\n')
            except KeyError:
                print("Key error")

if __name__ == '__main__':
    # main()
    json2strange()
