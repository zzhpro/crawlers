import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import requests

DEBUG = False

def get_main_table():
    url = 'https://zh.wikipedia.org/zh-my/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E6%94%BF%E9%BB%A8%E5%88%97%E8%A1%A8'
    options = Options()
    options.headless = not DEBUG
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    table_xpath = '/html/body/div[3]/div[3]/div[5]/div[1]/table[2]'
    lines = driver.find_element(By.XPATH, table_xpath).find_elements(By.TAG_NAME, 'tr')[1:]
    headers = ['id', 'ref', 'name', 'incharge', 'foundation', 'foundation1', 'foundation2']
    main_table = []
    citation_xpath = '/html/body/div[3]/div[3]/div[5]/div[1]/div[5]/ol'
    citation_list = driver.find_element(By.XPATH, citation_xpath).find_elements(By.TAG_NAME, 'li')
    for i, line in enumerate(lines):
        cols = line.find_elements(By.TAG_NAME, 'td')
        main_table.append({header:col.text.encode('utf8').decode() for (header, col) in zip(headers, cols)})
        ref_link = citation_list[i].find_element(By.TAG_NAME, 'cite').find_element(By.TAG_NAME, 'a').get_attribute('href')
        main_table[-1]['ref'] = ref_link
        try:
            wiki = cols[2].find_element(By.TAG_NAME, 'a') 
            main_table[-1]['wiki'] = wiki.get_attribute('href')
        except:
            pass
    with open("./twparties/main_table.json", "w", encoding='utf8') as fp:
        json.dump(main_table, fp, ensure_ascii=False)

def get_gov(driver, party_dir):
    data = {}
    title_list = driver.find_element(By.CLASS_NAME, 'party-title-list').find_elements(By.TAG_NAME, 'p')
    data['id'], data['name'], data['status'] = [t.text for t in  title_list]
    party_list = driver.find_element(By.CLASS_NAME, 'party-list').find_elements(By.TAG_NAME, 'li')
    party_list = party_list[:-1] # Do not include the last line "章程"
    ll = len(party_list)
    for ind, line in enumerate(party_list):
        key = line.find_element(By.TAG_NAME, 'h2').text
        if ind != len(party_list) - 1:
            value = line.find_element(By.TAG_NAME, 'p').text
        else:
            try:
                value = line.find_element(By.TAG_NAME, 'a').get_attribute('href')
            except:
                value = ''
        data[key] = value
    with open(os.path.join(party_dir, 'gov_data.json'), 'w', encoding='utf8') as fp:
        json.dump(data, fp, ensure_ascii=False)
    try:
        img_src = driver.find_element(By.CLASS_NAME, 'party-title-logo').find_element(By.TAG_NAME, 'img').get_attribute('src')
        proxies = {
            'http' : 'localhost:7890', 
            'https' : 'localhost:7890'
        }
        img = requests.get(img_src, proxies=proxies).content
        with open(os.path.join(party_dir, 'logo.jpg'), "wb") as fp:
            fp.write(img)
    except:
        pass


def get_wiki(driver, party_dir):
    data = {}
    table_xpath = '//*[@id="mw-content-text"]/div[1]/table[1]/tbody'
    intro_xpath = '//*[@id="mw-content-text"]/div[1]/p[1]'
    table = driver.find_element(By.XPATH, table_xpath)
    intro = driver.find_element(By.XPATH, intro_xpath).text

    data['intro'] = intro
    for tr in table.find_elements(By.TAG_NAME, 'tr'):
        try:
            th = tr.find_element(By.TAG_NAME, 'th').text
            td = tr.find_element(By.TAG_NAME, 'td').text
            data[th] = td
        except:
            pass

    with open(os.path.join(party_dir, 'wiki_data.json'), "w", encoding='utf8') as fp:
        json.dump(data, fp, ensure_ascii=False)

def get_gov_wiki():
    options = Options()
    options.headless = not DEBUG
    driver = webdriver.Chrome(options=options)

    data_dir = './twparties'
    with open('./twparties/main_table.json', "r", encoding='utf8') as f:
        main_table = json.load(f)
    
    for party in main_table:
        party_dir = os.path.join(data_dir, party['name'])
        if not os.path.exists(party_dir):
            os.mkdir(party_dir)
        if 'ref' in party:
            driver.get(party['ref'])
            get_gov(driver, party_dir)
        if 'wiki' in party:
            driver.get(party['wiki'])
            get_wiki(driver, party_dir)
        print("Done", party['name'])


if __name__ == '__main__':
    get_gov_wiki()
        
