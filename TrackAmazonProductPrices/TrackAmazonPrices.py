import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3 as sql
import pandas as pd

from products_url_list import urls

# Creating db connection in global scope
dbname = "ProductPrice.db"
con = sql.connect(dbname)
cursor = con.cursor()
# -----------------------------------------

def get_amazon_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }
    try:
        response = requests.get(url, headers = headers, timeout = 5)
    except Exception as e:
        print(e)
        return
    if response.ok:
        soup = BeautifulSoup(response.text, "lxml")
        
        prod_title = soup.find(id="productTitle").contents[0]
        prod_price = (soup.find(id="priceblock_ourprice").contents[0].encode('ascii', 'ignore')).decode("utf-8")

        return (prod_title.strip(), prod_price)
    else:
        print("Error Response: ", response.status_code)

def create_table(table, attributes):
    sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
    cursor.execute(sql)
    if cursor.fetchone() == None:
        table_structure = "".join(i+", " for i in [f"{key} {value}" for key,value in attributes.items()])[:-2]
        sql = f"CREATE TABLE {table}({table_structure})"
        try:
            cursor.execute(sql)
            print(f"\nTable({table}) created successfully!\n")
        except Exception as e:
            print(e)
    else:
        print("\nTable already exists!\n")



def insert_table(table, cols, vals):
    columns = "".join(i+", " for i in cols)[:-2]
    values = "".join(f"'{i}', " for i in vals)[:-2]
    sql = f"INSERT INTO {table}({columns}) VALUES({values})"
    try:
        cursor.execute(sql)
        con.commit()
        print(f"\nData inserted into {table} successfully!\n")
    except Exception as e:
        print(e)

def show_table(table):
    sql = f"SELECT * from {table}"
    df = pd.read_sql_query(sql, con)
    print(df)

def query_table(table, fields, condition = None):
    fields = "".join([f"{i}, " for i in fields])[:-2]
    if condition is None:
        sql = f"SELECT {fields} from {table}"
    else:
        sql = f"SELECT {fields} from {table} where {condition}"
    df = pd.read_sql_query(sql, con)
    return df

def delete_table():
    pass

def price_changed(table, product, price):
    df = query_table(table = table, fields = ["Price", "Date"], condition = f"Product = '{product}' ORDER BY Date DESC")
    if df.empty:
        return True
    elif df.loc[0, "Price"] != price:
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        table = "AmazonPrices"
        create_table(
            table = table,
            attributes = {
                "ID" : "INTEGER PRIMARY KEY AUTOINCREMENT",
                "Product" : "TEXT NOT NULL",
                "Date" : "TEXT NOT NULL",
                "Price" : "REAL NOT NULL"
                }
        )

        for url in urls:
            title , price = get_amazon_price(url)
            if price_changed(table, title, price):
                insert_table(table= table, cols = ['Product', 'Date', 'Price'], vals = [title, str(datetime.now()), price])
        
        show_table(table = table)            

    except Exception as e:
        print(e)
    finally:
        con.close()