import praw
import os
import json
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time

# Load environment variables
load_dotenv()

# Reddit credentials
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_agent = "RakshanRecipeCollector/1.0"

# Reddit client setup
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

# Target subreddit
subreddit = reddit.subreddit('recipes')

# File size constants
MAX_FILE_SIZE = 512 * 1024            # 0.5 MB per file
TOTAL_SIZE_LIMIT = 4 * 1024 * 1024    # 4 MB total

file_index = 0
current_size = 0
total_size = 0
posts_fetched = 0

# Output directory
os.makedirs("rakshan_data", exist_ok=True)
current_file = open(f'rakshan_data/rakshan_posts_{file_index}.json', 'w')

# Sources to fetch from
sources = [
    subreddit.top(time_filter='all', limit=None),
    subreddit.hot(limit=None),
    subreddit.new(limit=None)
]

for source in sources:
    for post in source:
        if total_size >= TOTAL_SIZE_LIMIT:
            break

        html_title = ""
        try:
            if post.url.startswith("http") and not post.url.endswith((".jpg", ".png", ".gif", ".pdf", ".jpeg")):
                response = requests.get(post.url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                if soup.title:
                    html_title = soup.title.string.strip()
        except Exception:
            html_title = ""

        post_data = {
            'title': post.title,
            'selftext': post.selftext,  # 🔥 added to boost post size
            'url': post.url,
            'created_utc': post.created_utc,
            'score': post.score,
            'author': str(post.author),
            'num_comments': post.num_comments,
            'permalink': post.permalink,
            'html_title': html_title
        }

        line = json.dumps(post_data) + "\n"
        line_size = len(line.encode('utf-8'))

        if current_size + line_size > MAX_FILE_SIZE:
            current_file.close()
            file_index += 1
            current_file = open(f'rakshan_data/rakshan_posts_{file_index}.json', 'w')
            current_size = 0
            print(f"🔁 Switched to file: rakshan_posts_{file_index}.json")

        current_file.write(line)
        current_size += line_size
        total_size += line_size
        posts_fetched += 1

        if posts_fetched % 25 == 0:
            print(f"{posts_fetched} posts fetched, file: rakshan_posts_{file_index}.json, file size: {current_size / 1024:.2f} KB")

        time.sleep(0.5)

# Finalize
current_file.close()
print(f"Data extraction complete. {posts_fetched} posts saved across {file_index + 1} files (~{total_size / 1024 / 1024:.2f} MB total).")
