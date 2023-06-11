import pandas as pd
from playwright.sync_api import sync_playwright
import mysql.connector

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print('OPENING BROWSER.....')
        page.goto('https://coinmarketcap.com/')
        page.wait_for_timeout(10000)

        # Scrolling down to allow data to load since it's loaded dynamically
        for i in range(5):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(4000)

        # Select the CSS selector for table rows
        tr_selector = 'div.cmc-body-wrapper table tbody tr'
        tr_list = page.query_selector_all(tr_selector)

        # Extracting data and processing from each table row
        data = []
        for tr in tr_list:
            rank_text = tr.query_selector('td:nth-child(2) p').inner_text()
            rank = int(rank_text)
            name = tr.query_selector('td:nth-child(3) p').inner_text()
            symbol = tr.query_selector('td:nth-child(3) p[color="text3"]').inner_text()
            price_text = tr.query_selector('td:nth-child(4) span').inner_text().replace('$', '').replace(',', '').replace('...', '000')
            price = float(price_text)
            market_cap_text = tr.query_selector('td:nth-child(8) span[class="sc-edc9a476-1 gqomIJ"]').inner_text().replace('$', '').replace(',', '')
            market_cap = float(market_cap_text)
            volume_text = tr.query_selector('td:nth-child(9) p').inner_text().replace('$', '').replace(',', '')
            volume = float(volume_text)

            data.append([rank, name, symbol, price, market_cap, volume])

        # Create DataFrame and export to CSV
        #columns = ['Rank', 'Name', 'Symbol', 'Price', 'Market_Cap(usd)', 'Volume_24h(usd))']
        #df = pd.DataFrame(data, columns=columns)
        #df.to_csv('crypto.csv', index=False)
        print('DATA EXTRACTED SUCCESSFULLY!!')


        cnx = mysql.connector.connect(
            host='localhost',  # Replace with your host
            user='root',  # Replace with your username
            #password='',  # Replace with your password
            database='crypto_database'
        )

        # Create a cursor object to execute SQL queries
        cursor = cnx.cursor()

        # Prepare the INSERT statement
        insert_query = "INSERT INTO crypto_table (`rank`, `name`, `symbol`, `price`, `market_cap`, `volume`) VALUES (%s, %s, %s, %s, %s, %s)"
        # Insert each row into the table
        for row in data:
            cursor.execute(insert_query, row)

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor and connection
        cursor.close()
        cnx.close()



        browser.close()

        print('DATA HAS BEEN INSERTED INTO DATABASE...')

if __name__ == '__main__':
    main()