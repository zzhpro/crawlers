from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import requests
import json
import os
import re


DEBUG = False

if os.name == 'nt':
    illegal_chars = r"[<>?/\\|:*\"]"
    root_path = 'C:\\Users\\15120\Desktop\\crawler\\mitcsail'
elif os.name == 'posix':
    illegal_chars = r"[/]"
    root_path = '/home/data/zhangzhenhao-21/crawlers/mitcsail/news'
else:
    raise ValueError("Unknown OS.")


def string_to_legal_filename(name):
    return re.sub(illegal_chars, "", name)


def got_img(d):
    return d.find_element(By.TAG_NAME, 'img').get_attribute('src')


def got_text(d):
    return d.find_elements(By.TAG_NAME, "p")


def xpath2list(d: webdriver, xpath: str):
    try:
        return [a.text for a in d.find_element(By.XPATH, xpath).find_elements(By.TAG_NAME, 'a')]
    except NoSuchElementException:
        return []


def crawl_news_page(url, driver: webdriver):
    # Load the web page
    driver.get(url)
    wait = WebDriverWait(driver, timeout=3)
    img_src = wait.until(got_img)
    text_tags = wait.until(got_text)
    # Create local folder
    title = driver.title.split('|')[0].strip()
    title = string_to_legal_filename(title)
    news_path = os.path.join(root_path, title)
    if not os.path.exists(news_path):
        os.makedirs(news_path)
    else:
        print("Skipped", title)
        return "Skipped"
    # Save the image
    img = requests.get(img_src).content
    img_name = "img." + img_src.split('.')[-1]
    with open(os.path.join(news_path, img_name), "wb") as f:
        f.write(img)
    # Save the text
    text = []
    for p in text_tags:
        text.append(p.text)
    text = '\n'.join(text)
    with open(os.path.join(news_path, "article.txt"), "w", encoding='utf8') as f:
        f.write(text)
    # Save the descriptive information
    date = driver.find_element(By.TAG_NAME, "time").get_attribute('datetime').split('T')[0]
    author = xpath2list(driver, '//h4[text()="Written By"]/..')
    people = xpath2list(driver, '//h4[text()="People"]/../div[1]')
    ra = xpath2list(driver, '//h4[text()="Research Areas"]/..')
    ia = xpath2list(driver, '//h4[text()="Impact Areas"]/..')
    info = {
        "date": date, "author": author, "people": people,
        "Research Areas": ra, "Impact Areas": ia
    }
    with open(os.path.join(news_path, "info.json"), "w") as f:
        json.dump(info, f)
    print("Finished", title)
    return "Done"


def crawl_news_links(url: str, n_loads: int, driver):
    driver.get(url)

    cards = []

    def got_more_cards(d):
        new_cards = d.find_elements(By.CLASS_NAME, "cs-news-result-card__card__content")
        return new_cards if len(new_cards) > len(cards) else []

    wait = WebDriverWait(driver, timeout=3)
    for i in range(n_loads):
        cards = wait.until(got_more_cards)
        lm_button = driver.find_element(By.CLASS_NAME, "cs-pager").find_element(By.TAG_NAME, "button")
        lm_button.click()

    return [card.find_element(By.TAG_NAME, "a").get_attribute("href") for card in cards]


def crawl_news(url, n_loads):
    # If not debugging, don't show the browser
    options = Options()
    options.headless = not DEBUG
    driver = webdriver.Chrome(options=options)
    links = crawl_news_links(url, n_loads, driver)
    for link in links:
        if crawl_news_page(link, driver) == "Skipped":
            break
    driver.quit()
    print("Done!")


if __name__ == '__main__':
    crawl_news("https://www.csail.mit.edu/news/", 1)
