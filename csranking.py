import os
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import json
import requests

DEBUG = False

def try_get(element, by, string):
    try:
        return element.find_element(by, string)
    except NoSuchElementException:
        return None


def deal_subtable(subtable):
    tr_list = subtable.find_elements(By.TAG_NAME, "tr")
    name_xpath = "./td[2]/small/a[1]"
    google_scholar_xpath = "./td[2]/small/a[img[@alt='Google Scholar']]"
    dblp_xpath = "./td[2]/small/a[img[@alt='DBLP']]"
    pubs_xpath = "./td[3]/small"
    adj_xpath = "./td[4]/small"

    subtable_list = []
    for idx in range(0, len(tr_list), 2):
        home = try_get(tr_list[idx], By.XPATH, name_xpath)
        google = try_get(tr_list[idx], By.XPATH, google_scholar_xpath)
        dblp = try_get(tr_list[idx], By.XPATH, dblp_xpath)
        area = try_get(tr_list[idx], By.CLASS_NAME, "areaname")
        pubs = try_get(tr_list[idx], By.XPATH, pubs_xpath)
        adj = try_get(tr_list[idx], By.XPATH, adj_xpath)

        res = dict()
        res['name'] = home.text if home else ''
        res['home'] = home.get_attribute('href') if home else ''
        res['area'] = area.text if area else ''
        res['google_scholar'] = google.get_attribute('href') if google else ''
        res['dblp'] = dblp.get_attribute('href') if dblp else ''
        res['pubs'] = pubs.text if pubs else ''
        res['adj'] = adj.text if pubs else ''
        subtable_list.append(res)
    
    return subtable_list

def got_table(driver):
    return driver.find_element(By.XPATH, "/html/body/div[5]/form/div/div[2]/div[2]/div/div/table/tbody")

def crawl(driver: webdriver.Chrome, url):
    driver.get(url)

    wait = WebDriverWait(driver, timeout=3)
    table = wait.until(got_table)

    name_xpath_template = './tr[{}]/td[2]/span[2]'
    country_xpath_template = './tr[{}]/td[2]/img'
    count_xpath_template = './tr[{}]/td[3]'
    faculty_xpath_template = './tr[{}]/td[4]'
    button_xpath_template = './tr[{}]/td[2]/span[1]'
    subtable_xpath_template = './tr[{}]/td/div/div/table/tbody'

    for i in range(100):
        # scroll to the end
        driver.execute_script('return document.querySelector("#success > div").scrollBy(0, 100)')

    wait = WebDriverWait(driver, timeout=3)
    table = wait.until(got_table)

    csranking, i = [], 0
    while True:
        name_xpath = name_xpath_template.format(str(3*i+1))
        try:
            name = table.find_element(By.XPATH, name_xpath).text
        except NoSuchElementException:
            break
        country_xpath = country_xpath_template.format(str(3*i+1))
        country = table.find_element(By.XPATH, country_xpath).get_attribute('src')
        country = country.split('.')[-2].split('/')[-1]
        count_xpath = count_xpath_template.format(str(3*i+1))
        count = table.find_element(By.XPATH, count_xpath).text
        faculty_xpath = faculty_xpath_template.format(str(3*i+1))
        faculty = table.find_element(By.XPATH, faculty_xpath).text
        button = table.find_element(By.XPATH, button_xpath_template.format(3*i+1))
        button.click()
        subtable_xpath = subtable_xpath_template.format(str(3*(i+1)))
        subtable = table.find_element(By.XPATH, subtable_xpath)
        subtable_list = deal_subtable(subtable)
        csranking.append({
            'id': i,
            'name': name, 'country': country, 'count': count, 'faculty': faculty,
            'subtable' : subtable_list
        })
        print("{}th univ '{}' finished".format(i, name))
        i += 1
            

    with open('csranking.json', "w", encoding='utf8') as fp:
        json.dump(csranking, fp, ensure_ascii=False)
        


if __name__ == '__main__':
    options = Options()
    options.headless = not DEBUG
    driver = webdriver.Chrome(options=options)

    url = 'https://csrankings.org/#/index?all&world'

    crawl(driver, url)