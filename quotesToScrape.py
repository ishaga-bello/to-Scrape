import requests
import dataset
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

db = dataset.connect("sqlite:///quotes.db")

authors_seen = set()
base_url = "http://quotes.toscrape.com/"

def clean_url(url):
    # will clean "/author/Steve-Martin" to "Steve-Martin"
    # using urljoin to make abs url
    url = urljoin(base_url, url)
    # use urlparse to get out the path part
    path = urlparse(url).path
    # now split the path by "/" and get second part
    # ex. "/author/Steve-Martin" --> ["", "author", "Steve-Martin"]

    return path.split("/")[2]

def scrape_quotes(bs):
    for quote in bs.select("div.quote"):
        quote_text = quote.find(class_="text").get_text(strip=True)
        quote_author_url = clean_url(quote.find(class_="author").find_next_sibling("a").get("href"))
        quote_tag_urls = [clean_url(a.get("href")) for a in quote.find_all("a", class_="tag")]
        authors_seen.add(quote_author_url)

        # store this quote and it's tags
        quote_id = db["quotes"].insert(
            {
            "text": quote_text,
            "author": quote_author_url,
            }
        )

        db["quote_tags"].insert_many(
            [{
                "quote_id": quote_id,
                "tag_id": tag } for tag in quote_tag_urls]
        )

def scrape_author(bs, author_id):
    author_name = bs.find(class_="author-title").get_text(strip=True)
    author_DOB = bs.find(class_="author-born-date").get_text(strip=True)
    author_DOB_loc = bs.find(class_="author-born-location").get_text(strip=True)
    author_desc = bs.find(class_="author-description").get_text(strip=True)

    db["authors"].insert(
        {
            "author_id": author_id,
            "name": author_name,
            "DOB": author_DOB,
            "DOB_location": author_DOB_loc,
            "description": author_desc
        }
    )

url = base_url
while True:
    print("Now scraping:", url)
    page = requests.get(url)
    bs = BeautifulSoup(page.text, "lxml")
    # scrape the quotes
    scrape_quotes(bs)

    # check if there is a next page
    next_page = bs.select("li.next > a")
    if not next_page or not next_page[0].get("href"): break
    url = urljoin(url, next_page[0].get("href"))

# now fetch the author information
for author_id in authors_seen:
    url = urljoin(base_url, "/author/" + author_id)
    print("Now scraping_author:", url)
    author_page = requests.get(url)
    bs = BeautifulSoup(author_page.text, "lxml")
    scrape_author(bs, author_id)