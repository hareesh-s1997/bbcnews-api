from flask import Flask, jsonify, request
import pymongo
import urllib.parse

app = Flask(__name__)  # Create the Flask app

# MongoDB connection parameters
username = "username_for_db"
password = "password_for_db_connection"  # Be sure to properly escape special characters

# Escape the username and password
escaped_username = urllib.parse.quote_plus(username)
escaped_password = urllib.parse.quote_plus(password)

# Initialize a MongoDB client and connect to your MongoDB database
client = pymongo.MongoClient(f"mongodb+srv://{escaped_username}:{escaped_password}@cluster1.jpb0evz.mongodb.net/")
database = client["webscraper_project"]  # Replace with your database name
collection = database["bbc_news"]  # Replace with your collection name

@app.route('/articles', methods=['GET'])
def get_articles():
    # Get query parameters from the request
    query_text = request.args.get('query_text', default='')
    case_insensitive = request.args.get('case_insensitive', default=False, type=bool)

    # Construct the MongoDB query based on the query parameters
    if case_insensitive:
        query = {"headline": {"$regex": query_text, "$options": "i"}}
    else:
        query = {"headline": {"$regex": query_text}}

    cursor = collection.find(query)
    articles = []

    for document in cursor:
        article = {
            "author_name": document["author_name"],
            "headline": document["headline"],
            "article_url": document["article_url"],
            "article_text": document["article_text"]
        }
        articles.append(article)

    return jsonify(articles)

if __name__ == '__main__':
    app.run(host="0.0.0.0")