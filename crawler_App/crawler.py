import praw
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
reddit_username = os.getenv("REDDIT_USERNAME")
reddit_password = os.getenv("REDDIT_PASSWORD")
user_agent = "RecipeDataCollector/1.0 by Testing"

# Initialize Reddit client with your credentials
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

# Access the r/recipes subreddit
subreddit = reddit.subreddit('recipes')

# Open a file to store the data
with open('recipes_posts.json', 'w') as outfile:
    # Fetch posts in batches (handle pagination)
    for post in subreddit.top(limit=30):  # Adjust 'limit' as needed
        post_data = {
            'title': post.title,
            'url': post.url,
            'created_utc': post.created_utc,
            'score': post.score,
            'author': str(post.author),
            'num_comments': post.num_comments,
            'permalink': post.permalink
        }
        json.dump(post_data, outfile)
        outfile.write("\n")  # Write each post on a new line

        # Delay between requests to avoid hitting rate limits
        time.sleep(2)

print("Data extraction complete.")
