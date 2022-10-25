# Books and quotes to scrape from a light JavaScript website

## Books
The objective was to create a crawler that could go through the 100 pages of the different books listed on the website and for each book we wanted it's name, price, availabilty, author and genre.
One nifty trick that was performed here was to use [dataset](https://pypi.org/project/dataset/) 
--a simple library that allowed for rapid databases manipulation without much looking into the SQL part-- 
to create a crawler that was sortof intelligent and every time we run the scraper we are asked if we want to recrawl the site for new listings or just scrape the listings we have already stored (super cool !!!)

## Quotes
Scraping the quote site was a little bit easier as most of the info was just basic texts
