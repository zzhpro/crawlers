import enum
from tkinter import E
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import json
import time
import random
import psycopg2


DEBUG = False

area_names = [
    'natural_language_processing',
    'computer_vision',
    'machine_learning',
    'operating_systems',
    'distributed_systems',
    'networks',
    'databases',
    'computer_graphics',
    'compilers',
    'cryptography',
    'computer_architecture',
    'algorithms',
    'theoretical_computer_science',
    'computer_security',
    'cloud_computing',
    'internet_of_things',
    'software_engineering',
    'high_performance_computing'
]
base_url = 'https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=label:'

kMaxPagesPerArea = 2
kMaxPapersPerScholar = 5
kMaxCoauthorsPerScholar = 3

suid2sid = dict()
pname2pid = dict()

def random_sleep():
    time.sleep(random.randint(2, 8))

def try_find(element, by, metric):
    try:
        return element.find_element(by, metric)
    except NoSuchElementException:
        return None


def execution_engine(driver, config):
    driver.get(config['url'])
    wait = WebDriverWait(driver, 3)
    wait.until(config['wait_cond'])
    out_dict = {}
    for d in config['elements']:
        tag  = try_find(driver, By.XPATH, d['xpath'])
        out_dict[d['key']] = d['output'](tag)
    return out_dict


def crawl_paper(driver, url, cursor):
    config = {
        "url": url,
        "wait_cond": lambda d:d.find_elements(By.XPATH, '//*[@id="gsc_oci_title"]/a'),
        "elements": [
            {
                'key':  'title',
                'xpath': '//*[@id="gsc_oci_title"]/a',
                'output': lambda tag: tag.text if tag else None
            },
            {
                "key": 'author',
                'xpath': '//*[@id="gsc_oci_table"]/div[@class="gs_scl"][div[text()="Authors"]]/div[@class="gsc_oci_value"]',
                'output': lambda tag: tag.text if tag else None
            },
            {
                "key": 'date',
                'xpath': '//*[@id="gsc_oci_table"]/div[@class="gs_scl"][div[text()="Publication date"]]/div[@class="gsc_oci_value"]',
                'output': lambda tag: tag.text if tag else None
            },
            {
                "key": 'journal',
                'xpath': '//*[@id="gsc_oci_table"]/div[@class="gs_scl"][div[text()="Conference" or text()="Journal" or text()="Book"]]/div[@class="gsc_oci_value"]',
                'output': lambda tag: tag.text if tag else None
            },
            {
                "key": 'publisher',
                'xpath': '//*[@id="gsc_oci_table"]/div[@class="gs_scl"][div[text()="Publisher"]]/div[@class="gsc_oci_value"]',
                'output': lambda tag: tag.text if tag else None
            },
            {
                "key": 'description',
                'xpath': '//*[@id="gsc_oci_table"]/div[@class="gs_scl"][div[text()="Description"]]/div[@class="gsc_oci_value"]',
                'output': lambda tag: tag.text if tag else None
            },
            {
                "key": 'cited_by',
                'xpath': '//*[@id="gsc_oci_table"]/div[@class="gs_scl"][div[text()="Total citations"]]/div[@class="gsc_oci_value"]//a',
                'output': lambda tag: eval(tag.text.strip().split(' ')[-1]) if tag else None
            },
            {
                "key": 'pdf_src',
                'xpath': '//*[@id="gsc_oci_title_gg"]/div/a',
                'output':lambda tag: tag.get_attribute('href') if tag else None
            },
        ]
    }
    out_dict = execution_engine(driver, config)
    pid = pname2pid[out_dict['title']]
    sql = """
        insert into gs_paper values 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (pid, out_dict['title'], out_dict['author'], out_dict['date'], out_dict['journal'], 
        out_dict['publisher'], out_dict['description'], out_dict['cited_by'], out_dict['pdf_src']))
    # print((pid, out_dict['title'], out_dict['author'], out_dict['date'], out_dict['journal'], 
    #     out_dict['publisher'], out_dict['description'], out_dict['cited_by'], out_dict['pdf_src']))



def crawl_papers(driver, paper_list, cursor):
    cursor.execute("select max(id) from gs_paper;")
    last_finished = cursor.fetchone()[0]
    if last_finished is None:
        last_finished = -1
    for paper in paper_list[last_finished+1:]:
        random_sleep()
        try:
            crawl_paper(driver, paper, cursor)
        except NoSuchElementException:
            print("Skipping {} because of no such element exception".format(paper))
        except TimeoutException:
            print("Skipping {} because of timeout exception".format(paper))
        except KeyError:
            print("Skipping {} because of key error".format(paper))
        except:
            print("Skipping {} because of unknown exception".format(paper))


def crawl_scholar(driver: webdriver.Chrome, url, cursor, coa_list=None):
    suid = url.split('user=')[-1]
    sid = suid2sid[suid]
    paper_xpath = '//*[@id="gsc_a_b"]/tr'
    name_xpath = '//*[@id="gsc_prf_in"]'
    occup_xpath = '//*[@id="gsc_prf_i"]/div[2]'
    home_xpath = '//*[@id="gsc_prf_ivh"]/a'
    area_list_xpath = '//*[@id="gsc_prf_int"]'
    cite_xpath = '//*[@id="gsc_rsb_st"]/tbody/tr[1]/td[2]'
    i10index_xpath = '//*[@id="gsc_rsb_st"]/tbody/tr[2]/td[2]'
    hindex_xpath = '//*[@id="gsc_rsb_st"]/tbody/tr[3]/td[2]'
    paper_table_xpath = '//*[@id="gsc_a_b"]'
    img_xpath = '//*[@id="gsc_prf_pup-img"]'
    showmore_button_xpath = '//*[@id="gsc_bpf_more"]'

    scholar_sql = """
        insert into gs_scholar values
        (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    scholar_paper_sql = """
        insert into gs_scholar_paper values
        (%s, %s);
    """


    driver.get(url)
    wait = WebDriverWait(driver, timeout=3)
    wait.until(
        lambda d:d.find_element(By.XPATH, paper_xpath + '[last()]')
    )
    # Locate
    showmore_button = try_find(driver, By.XPATH, showmore_button_xpath)
    if showmore_button is not None:
        showmore_button.click()
    name_tag = try_find(driver, By.XPATH, name_xpath)
    occup_tag = try_find(driver, By.XPATH, occup_xpath)
    home_tag = try_find(driver, By.XPATH, home_xpath)
    area_list_tag = try_find(driver, By.XPATH, area_list_xpath)
    cite_tag = try_find(driver, By.XPATH, cite_xpath)
    i10index_tag = try_find(driver, By.XPATH, i10index_xpath)
    hindex_tag = try_find(driver, By.XPATH, hindex_xpath)
    paper_table_tag = try_find(driver, By.XPATH, paper_table_xpath)
    img_tag = try_find(driver, By.XPATH, img_xpath)

    # Extract
    sname = name_tag.text if name_tag else "NULL"
    occup = occup_tag.text if occup_tag else "NULL"
    home = home_tag.get_attribute('href') if home_tag else "NULL"
    area = ','.join(a.text for a in area_list_tag.find_elements(By.TAG_NAME, "a")) if area_list_tag else "NULL"
    cite = eval(cite_tag.text) if cite_tag else "NULL"
    i10index = eval(i10index_tag.text) if i10index_tag else "NULL"
    hindex = eval(hindex_tag.text) if hindex_tag else "NULL"
    img_src = img_tag.get_attribute("src") if img_tag else "NULL"
    paper_links = []
    all_papers =  paper_table_tag.find_elements(By.XPATH, ".//a[@class='gsc_a_at']")
    for tag in all_papers[:kMaxPapersPerScholar]:
        pname = tag.text
        if pname in pname2pid:
            pid = pname2pid[pname]
        else:
            pid = pname2pid[pname] = len(pname2pid)
            paper_links.append(tag.get_attribute('href'))
        cursor.execute(scholar_paper_sql, (sid, pid))
    cursor.execute(scholar_sql, (
        sid, sname, occup, home, area, cite, i10index, hindex, img_src
    ))
    if coa_list is not None:
        # Deal with his/her co-authors
        coa_button_xpath = '//*[@id="gsc_coauth_opn"]'
        coa_table_xpath = '//*[@id="gsc_codb_content"]'
        coa_button = try_find(driver, By.XPATH, coa_button_xpath)
        if coa_button:
            coa_button.click()
            coa_table = wait.until(
                lambda d:d.find_element(By.XPATH, coa_table_xpath)
            )
            if coa_table:
                tag_list = coa_table.find_elements(By.XPATH, "./div[@class='gsc_ucoar gs_scl']")
                for tag in tag_list[:kMaxCoauthorsPerScholar]:
                    coa_name_tag = try_find(tag, By.XPATH, ".//h3[@class='gs_ai_name']/a")
                    if coa_name_tag is None:
                        continue
                    surl = coa_name_tag.get_attribute('href')
                    suid = surl.strip().split('user=')[-1]
                    if suid in suid2sid:
                        coa_sid = suid2sid[suid]
                    else:
                        coa_list.append(surl)
                        coa_sid = suid2sid[suid] = len(suid2sid)
                    cursor.execute("insert into gs_coauthor values (%s, %s)", (sid, coa_sid))
    print("Done {}".format(sname))
    return paper_links


def crawl_scholars(driver, scholar_list, cursor):
    # Find out where we left up last time
    cursor.execute("select max(id) from gs_scholar;")
    last_finished = cursor.fetchone()[0]
    if last_finished is None:
        last_finished = -1
    # Deal with top scholars
    paper_list, coa_list = [], []
    for link in scholar_list[last_finished+1:]:
        random_sleep()
        try:
            tlist = crawl_scholar(driver, link, cursor, coa_list=coa_list)
            paper_list.extend(tlist)
        except NoSuchElementException:
            print("Skipping {} because of no such element exception".format(link))
        except TimeoutException:
            print("Skipping {} because of timeout exception".format(link))
        except KeyError:
            print("Skipping {} because of key error".format(link))
        except:
            print("Skipping {} because of unknown exception".format(link))

    # Deal with their co-authors
    for coa_link in coa_list:
        random_sleep()
        try:
            tlist = crawl_scholar(driver, coa_link, cursor)
            paper_list.extend(tlist)
        except NoSuchElementException:
            print("Skipping {} because of no such element exception".format(coa_link))
        except TimeoutException:
            print("Skipping {} because of timeout exception".format(coa_link))
        except KeyError:
            print("Skipping {} because of key error".format(coa_link))
        except:
            print("Skipping {} because of unknown exception".format(coa_link))

    return paper_list


def crawl_area(driver, aid, cursor):
    area_name = area_names[aid]
    url = base_url + area_name
    scholars_xpath = "//div[@class='gsc_1usr']"
    button_xpath = '//*[@id="gsc_authors_bottom_pag"]/div/button[2]'
    insert_as_sql = '''
        insert into gs_area_scholar values
        (%s, %s, %s)
    '''

    links, rank = [], 1
    driver.get(url)
    for tt in range(kMaxPagesPerArea):
        # Wait until the last scholar of this page was loaded
        wait = WebDriverWait(driver, timeout=3)
        wait.until(
            lambda d:d.find_element(By.XPATH, scholars_xpath + '[last()]')
        )
        # Get the scholars
        for scholar in driver.find_elements(By.XPATH, scholars_xpath):
            # Locate
            name_tag = try_find(scholar, By.XPATH, ".//h3[@class='gs_ai_name']/a")
            # Extract
            link = name_tag.get_attribute('href') if name_tag else  "NULL"
            suid = link.strip().split('user=')[1]
            # Store
            if suid not in suid2sid:
                sid = suid2sid[suid] = len(suid2sid)
                links.append(link)
            else:
                sid = suid2sid[suid]
            
            cursor.execute(insert_as_sql, (aid, sid, rank))
            rank += 1
        # Click on the button
        button = try_find(driver, By.XPATH, button_xpath)
        if tt == kMaxPagesPerArea - 1 or button is None:
            break
        button.click()


    print("Got {} new scholars for {}".format(len(links), area_name))
    return links


def crawl_areas(driver, cursor):
    scholar_links = []
    for idx in range(len(area_names)):
        area_links = crawl_area(driver, idx, cursor)
        scholar_links.extend(area_links)
    print("Done crawl areas")
    return scholar_links

def clear_all(cursor):
    sql = 'delete from {};'
    for relname in ['gs_area', 'gs_area_scholar', 'gs_scholar', 'gs_scholar_paper', 'gs_coauthor']:
        cursor.execute(sql.format(relname))


def insert_areas(cursor):
    sql = "insert into gs_area values (%s, %s)"
    for idx, name in enumerate(area_names):
        cursor.execute(sql, (idx, name))

def main():
    options = Options()
    options.headless = not DEBUG
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)

    conn = psycopg2.connect("host=10.105.222.6 port=41466 password=Ccxl2g5[7s+Y}tYF^^jaSg{6 dbname=crawler user=zzh")
    conn.autocommit = True
    cursor = conn.cursor()

    global suid2sid, pname2pid

    if not os.path.exists("./scholar_list.json"):
        clear_all(cursor)
        insert_areas(cursor)
        scholar_list = crawl_areas(driver, cursor)
        with open("./scholar_list.json", "w", encoding='utf8') as fp:
            json.dump(scholar_list, fp, ensure_ascii=False)
        with open("./suid2sid.json", "w", encoding='utf8') as fp:
            json.dump(suid2sid, fp, ensure_ascii=False)
    else:
        with open("./scholar_list.json", "r", encoding='utf8') as fp:
            scholar_list = json.load(fp)
        with open("./suid2sid.json", "r", encoding='utf8') as fp:
            suid2sid = json.load(fp)

    if not os.path.exists("./paper_list.json"):
        paper_list = crawl_scholars(driver, scholar_list, cursor)
        with open("./paper_list.json", "w", encoding='utf8') as fp:
            json.dump(paper_list, fp, ensure_ascii=False)
        with open("./pname2pid.json", "w", encoding='utf8') as fp:
            json.dump(pname2pid, fp, ensure_ascii=False)
    else:
        with open("./paper_list.json", "r", encoding='utf8') as fp:
            paper_list = json.load(fp)
        with open("./pname2pid.json", "r", encoding='utf8') as fp:
            pname2pid = json.load(fp)
    
    crawl_papers(driver, paper_list, cursor)

    # global panme2pid
    # pname2pid['XORs in the air: Practical wireless network coding'] = 0
    # crawl_paper(driver, 'https://scholar.google.com/citations?view_op=view_citation&hl=en&user=nst5fHgAAAAJ&citation_for_view=nst5fHgAAAAJ:u-x6o8ySG0sC', cursor)


    cursor.close()
    conn.close()

    print("All Done!!!")

if __name__ == '__main__':
    main()