import requests
from bs4 import BeautifulSoup
import pymongo
import urllib.parse
from urllib.parse import urlparse, urljoin

# Function to scrape and store BBC articles in MongoDB
def scrape_and_store_bbc_articles(request):
    # Define the URL of the BBC News page you want to scrape
    url = "https://www.bbc.com/news"

    # Send an HTTP GET request to the BBC News page
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize a MongoDB client and connect to the database
        client = pymongo.MongoClient("mongodb+srv://username:" + urllib.parse.quote("password") + "@cluster1.jpb0evz.mongodb.net/")
        database = client["webscraper_project"]  # Replace with your database name
        collection = database["bbc_news"]  # Replace with your collection name

        # Extract and store article details
        articles = soup.find_all('div', class_='gs-c-promo')
        for article in articles:
            title = article.find('h3').text.strip()
            link = article.find('a')['href']
            parsed_url = urlparse(link)
            if not parsed_url.scheme:
                link = urljoin(url, link)

            # Check if the article URL already exists in the collection
            if not collection.find_one({"article_url": link}):
                # Send an HTTP GET request to the article page
                article_response = requests.get(link)
                if article_response.status_code == 200:
                    # Parse the HTML content of the article page
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')

                    # Extract the text content of the article
                    article_elements = article_soup.find_all('p')
                    article_text = '\n'.join([element.get_text() for element in article_elements])

                    # Extract the author's name
                    author_match = article_soup.find('a', class_='author-unit__text b-font-family-serif')
                    author_element = article_soup.find('div', class_='ssrcss-68pt20-Text-TextContributorName')
                    if author_element:
                        author = author_element.text.strip()
                        author = author.lstrip("By ")
                    elif author_match:
                        author = author_match.text.strip()
                        author = author.lstrip("By ")
                    else:
                        author = "Unknown Author"

                    # Insert data into MongoDB collection
                    article_data = {
                        "article_text": article_text,
                        "author_name": author,
                        "headline": title,
                        "article_url": link
                    }
                    collection.insert_one(article_data)

        # Close the MongoDB client
        client.close()
        print("Articles scraped and stored in MongoDB.")
    else:
        print("Failed to retrieve the BBC News page.")
    
    return f"done"
