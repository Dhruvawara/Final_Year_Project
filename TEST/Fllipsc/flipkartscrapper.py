import os
import time
from multiprocessing import Pool
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

delays = [7, 4, 6, 2, 10, 5]
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.106 Safari/537.36',
           'referrer': 'https://flipkart.com'
           }
start_time = time.time()
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--incognito')
chrome_options.add_argument("--headless")


def get_links(url):
    page = requests.get(url, headers=headers, timeout=5)
    soup = BeautifulSoup(page.text, 'lxml')
    print(soup.title.text)  # added
    div = soup.find_all('div', attrs={'class': '_2MImiq _1Qnn1K'})
    for i in div:
        span = i.findChildren('span', recursive=True)
        total_page = span[0]
    last_page = int(total_page.text[5:].split()[2])
    print('Total number of pages is: ', last_page)
    pages = []
    if last_page != '1':
        for i in range(1, last_page+1):
            pages.append(url + '&page=' + str(i))
    return pages


def open_review_page(url):
    page = requests.get(url, headers=headers, timeout=2)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(soup.title.text)  # added
    # all_reviews_link = soup.find(
    #     'div', attrs={'class': 'col _39LH-M'}).find('a', recursive=False).get('href')
    if soup.find('div', attrs={'class': 'col JOpGWq'}) is None:
        all_reviews_link = soup.find('div', attrs={'class': 'col JOpGWq'}).find(
            'a', recursive=False).get('href')
    else:
        all_reviews_link = soup.find(
            'div', attrs={'class': 'col JOpGWq'}).find('a', recursive=False).get('href')
    all_reviews_link = 'https://www.flipkart.com' + all_reviews_link
    return all_reviews_link


def write_to_csv(data):
    if not os.path.isfile('./scrapped_data.csv'):
        data.to_csv('./scrapped_data.csv', index=False)
    else:
        with open('./scrapped_data.csv', 'a') as file:
            data.to_csv(file, header=False, index=False)
            file.close()


def parse(url):
    delay = np.random.choice(delays)
    time.sleep(delay)
    driver = webdriver.Chrome(
        "D:\Final_Year_Project\TEST\Fllipsc\chromedriver.exe")  # change path
    driver.get(url)
    driver.find_elements_by_link_text('READ MORE')
    read_more_buttons = driver.find_elements_by_class_name('_1AtVbE')
    for x in range(len(read_more_buttons)):
        driver.execute_script("arguments[0].click();", read_more_buttons[x])
        time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.close()
    driver.quit()
    titles_elements = soup.find_all('p', attrs={'class': '_2-N8zT'})
    username_elements = soup.find_all('p', attrs={'class': '_2sc7ZR _2V5EHH'})
    usernames = [user.get_text() for user in username_elements]
    timestamps = [usernames[i] for i in range(len(usernames)) if i % 2 != 0]
    del usernames[1::2]
    rating_element = soup.find_all('div', attrs={'class': '_3LWZlK _1BLPMq'})
    ratings = [t.get_text() for t in rating_element]
    del ratings[0]
    if len(titles_elements) == 0:
        review_text_elements = soup.find_all('div', attrs={'class': 't-ZTKy'})
        review_text = [review.get_text() for review in review_text_elements]
        data = {'Username': usernames, 'Rating': ratings,
                'Review': review_text, 'Timestamp': timestamps}
    else:
        titles = [title.get_text() for title in titles_elements]
        review_text_elements = soup.find_all('div', attrs={'class': 't-ZTKy'})
        review_text = [review.get_text().replace('READ MORE', '')
                       for review in review_text_elements]
        data = {'Username': usernames, 'Rating': ratings, 'Title': titles, 'Review': review_text,
                'Timestamp': timestamps}
    review_data = pd.DataFrame().from_dict(data)
    write_to_csv(review_data)


if __name__ == '__main__':

    print("Enter url with one space at the end:")
    url = input()[:-1:]
    reviews_link = open_review_page(url)
    pages = get_links(reviews_link)
    print(len(pages))  # added
    with Pool(1) as p:
        p.map(parse, pages)
    print("--- %s seconds ---" % (time.time() - start_time))
