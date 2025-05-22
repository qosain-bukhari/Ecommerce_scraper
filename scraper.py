import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = 'https://books.toscrape.com/'
session = requests.Session()

def get_categories():
    res = session.get(base_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    category_list = soup.select('.side_categories ul li ul li a')
    categories = {cat.text.strip(): base_url + cat['href'] for cat in category_list}
    return categories

def get_rating(tag):
    classes = tag.get('class', [])
    for c in classes:
        if c != 'star-rating':
            return c
    return 'No rating'

def scrape_category(name, url):
    print(f"📦 Scraping category: {name}")
    page_url = url
    books = []

    while True:
        res = session.get(page_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('article.product_pod')

        for item in items:
            title = item.h3.a['title']
            price = item.find('p', class_='price_color').text.strip()
            stock = item.find('p', class_='instock availability').text.strip()
            rating = get_rating(item.p)
            product_url = base_url + item.h3.a['href'].replace('../../../', 'catalogue/')

            books.append({
                'Title': title,
                'Price (£)': price,
                'Stock': stock,
                'Rating': rating,
                'Category': name,
                'Product URL': product_url
            })

        next_btn = soup.select_one('li.next a')
        if next_btn:
            page_url = url.rsplit('/', 1)[0] + '/' + next_btn['href']
            time.sleep(1)
        else:
            break

    return books

def scrape_all_categories():
    all_books = []
    categories = get_categories()
    for name, url in categories.items():
        all_books.extend(scrape_category(name, url))
    return all_books

if __name__ == '__main__':
    data = scrape_all_categories()
    df = pd.DataFrame(data)
    df.to_csv('books.csv', index=False)
    df.to_json('books.json', orient='records', indent=2)
    df.to_excel('books.xlsx', index=False)
    print("✅ Data scraping completed and saved.")
