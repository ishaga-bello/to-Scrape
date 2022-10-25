import requests 
import dataset
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

db = dataset.connect("sqlite:///books1.db")

base_url = "http://books.toscrape.com/"

def scrape_books(bs, url):
    for book in bs.select("article.product_pod"):

        book_url = book.find("h3").find("a").get("href")
        book_url = urljoin(url, book_url)

        path = urlparse(book_url).path
        book_id = path.split("/")[2]
        # upsert tries to update first and then insert instead
        db["books"].upsert({
            "book_id": book_id,
            "last_seen": datetime.now()
        }, ["book_id"])

def scrape_book(bs, book_id):
    main = bs.find(class_="product_main")
    book = {}
    book["book_id"] = book_id
    book["title"] = main.find("h1").get_text(strip=True)
    
    price = main.find(class_="price_color").get_text(strip=True)
    price = re.sub("^(Â£)", "", price)
    book["price"] = price
    book["stock"] = main.find(class_="availability").get_text(strip=True)
    book["rating"] = " ".join(main.find(class_="star-rating").get("class")).replace("star-rating", "").strip()
    book["img"] = bs.find(class_="thumbnail").find("img").get("src")
    desc = bs.find(id="product_description")
    book["description"] = ""
    if desc: book["description"] = desc.find_next_sibling("p").get_text(strip=True)

    info_table = bs.find("table")
    for row in info_table.find_all("tr"):
        header = row.find("th").text

        # since we are using the header as a column
        # clean it a bit for sqlite
        header = re.sub("[^a-zA-Z]+", "_", header)
        value = row.find("td").text
        book[header] = value
    
    db["book_info"].upsert(book, ["book_id"])

# scrape the pages in catalogue
url = base_url
inp = input("do you wish to re scrape the catalogue y/n: --> ").lower()

while True and inp == "y":
    print("Now scraping page:", url)
    r = requests.get(url)
    bs = BeautifulSoup(r.text, "lxml")
    scrape_books(bs, url)

    # is there a next page?
    next_a = bs.find(class_="next").find("a").get("href")
    if not next_a: break

    url = urljoin(url, next_a)

# now scrape book by book starting by the oldest first
books = db["books"].find(order_by=['last_seen'])

for book in books:
    book_id = book["book_id"]
    book_url = base_url + "catalogue/{}".format(book_id)
    print("Now scraping book", book_url)
    r = requests.get(book_url)
    # r.encoding = "utf-8"
    bs = BeautifulSoup(r.text, "lxml")
    scrape_book(bs, book_id)

    # update the last seen timestamp
    db["books"].upsert({
        "book_id": book_id,
        "last_seen": datetime.now()
    }, ["book_id"])