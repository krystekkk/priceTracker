from datetime import datetime, timedelta
from send_email import send_email
import time
import schedule
import requests
import bs4
import re
import sqlite3
import os
import logging


base_url = 'https://www.amazon.pl/dp/'

products_list = ['B0CHXP4DN5', 'B07W6JLFZ7', 'B07W6H8CMV']

price_limits = {
    'B0CHXP4DN5': 3401,
    'B07W6JLFZ7': 201,
    'B07W6H8CMV': 703,
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}
response = requests.get(base_url, headers=headers)
cookies = response.cookies


def create_database():
    with sqlite3.connect('prices.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                name TEXT,
                url TEXT,
                price REAL,
                date DATETIME
            )
        ''')
        conn.commit()


def insert_data_to_database(product_id, name, url, price, date):
    with sqlite3.connect('prices.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prices(product_id, name, url, price, date) VALUES (?, ?, ?, ?, ?)',
                       (product_id, name, url, price, date)
                       )
        conn.commit()


def fetch_data_from_database():
    with sqlite3.connect('prices.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prices')
        return cursor.fetchall()


def track_prices(last_notification, now):

    time_difference = now - last_notification

    for product in products_list:
        try:
            product_response = requests.get(base_url + product, headers=headers, cookies=cookies)
            soup = bs4.BeautifulSoup(product_response.text, features='lxml')
            price_lines = soup.findAll(class_="a-price-whole")
            price_fraction = soup.findAll(class_="a-price-fraction")
            product_title = soup.find_all(id="productTitle")

            title = str(product_title[0])
            title = title.replace('<span class="a-size-large product-title-word-break" id="productTitle">        ', '')
            title = title.replace('       </span>', '')

            final_price = str(price_lines[0])
            final_price = final_price.replace('<span class="a-price-whole">', '')
            final_price = final_price.replace('<span class="a-price-decimal">,</span></span>', '')
            final_price = re.sub(r"\s+", "", final_price, flags=re.UNICODE)

            fraction = str(price_fraction[0])
            fraction = fraction.replace('<span class="a-price-fraction">', '')
            fraction = fraction.replace('</span>', '')
            fraction = re.sub(r"\s+", "", fraction, flags=re.UNICODE)

            final_price = final_price + "." + fraction
            final_price = float(final_price)

            scraping_date = datetime.now()
            # print(scraping_date)
            print(base_url + product)
            print(title)
            print(final_price)
            print('----------------------------------------------')

            if final_price <= price_limits[product]:
                if time_difference >= timedelta(days=7):
                    send_email(base_url + product, final_price, price_limits[product])
                    logging.info("Email sent.")
                # TODO: make email notifications more smart, for example if an email is already sent first day,
                #  do not send it next day.
                #  Store notifications details in database to control previous notification date

            insert_data_to_database(product, title, base_url + product, final_price, scraping_date)

        except IndexError:
            # TODO: retake function
            pass


if __name__ == '__main__':
    logging.basicConfig(
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO
    )

    last_notification = datetime(2024, 12, 9, 10, 0, 0)
    now = datetime.now()

    if not os.path.exists('prices.db'):
        logging.info("Creating database")
        create_database()
    # print(fetch_data_from_database())
    logging.info("Start scraping")
    track_prices(last_notification, now)
    schedule.every(1).minutes.do(track_prices)

    while True:
        schedule.run_pending()
        time.sleep(1)
