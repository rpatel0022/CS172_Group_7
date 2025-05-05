import praw
import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load Reddit API credentials
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_agent = "RakshanRecipeCollector/1.0"
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

# Config
MAX_FILE_SIZE = 10 * 1024 * 1024         # 10 MB
TOTAL_SIZE_LIMIT = 20 * 1024 * 1024     # 500 MB
OUTPUT_DIR = "rushi_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_next_file_index(prefix):
    files = os.listdir(OUTPUT_DIR)
    pattern = re.compile(rf'{re.escape(prefix)}_(\d+)\.json')
    indexes = [int(m.group(1)) for f in files if (m := pattern.match(f))]
    return max(indexes) + 1 if indexes else 0

def fetch_html_title(url):
    try:
        if url.startswith("http") and not url.endswith((".jpg", ".png", ".gif", ".pdf", ".jpeg")):
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return soup.title.string.strip() if soup.title else ""
    except:
        return ""
    return ""

def crawl_subreddit(subreddit_name):
    try:
        print(f"\n🟡 Starting r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)
        sources = [
            subreddit.top(time_filter='all', limit=None),
            subreddit.hot(limit=None),
            subreddit.new(limit=None)
        ]

        file_prefix = f"{subreddit_name}_posts"
        file_index = get_next_file_index(file_prefix)
        current_file = open(os.path.join(OUTPUT_DIR, f"{file_prefix}_{file_index}.json"), 'w')
        current_size = 0
        total_size = 0
        posts_fetched = 0

        for source in sources:
            for post in source:
                if total_size >= TOTAL_SIZE_LIMIT:
                    print(f"⛔ Reached total size limit of 500 MB for r/{subreddit_name}")
                    break

                post_data = {
                    'title': post.title,
                    'selftext': post.selftext,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'score': post.score,
                    'author': str(post.author),
                    'num_comments': post.num_comments,
                    'permalink': post.permalink,
                    'html_title': fetch_html_title(post.url)
                }

                line = json.dumps(post_data) + "\n"
                line_size = len(line.encode('utf-8'))

                if current_size + line_size > MAX_FILE_SIZE:
                    current_file.close()
                    file_index += 1
                    current_file = open(os.path.join(OUTPUT_DIR, f"{file_prefix}_{file_index}.json"), 'w')
                    current_size = 0
                    print(f"🔁 Switched to new file: {file_prefix}_{file_index}.json")

                current_file.write(line)
                current_size += line_size
                total_size += line_size
                posts_fetched += 1

                if posts_fetched % 25 == 0:
                    print(f"📥 {subreddit_name}: {posts_fetched} posts, file: {file_prefix}_{file_index}.json, size: {current_size / 1024:.2f} KB")

                time.sleep(0.25)  # throttle to avoid rate limit

        current_file.close()
        print(f"Finished r/{subreddit_name}: {posts_fetched} posts, {file_index + 1} files, ~{total_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"Error in r/{subreddit_name}: {e}")

# List of subreddits from your screenshots
# subreddits = [
#     "FoodPorn",           # High-quality pictures of food
#     "ShittyFoodPorn",     # Funny and bad-looking food pics
#     "EatCheapAndHealthy", # Budget-friendly healthy meals
#     "FoodHacks",          # Food tricks and shortcuts
#     "nutrition",          # Discussions about diet and nutrition
#     "fastfood",           # Fast food news and reviews
#     "TopSecretRecipes",   # Reverse-engineered famous brand recipes
#     "veganrecipes",       # Plant-based recipe sharing
#     "fitmeals",           # Fitness-oriented meals and meal prep
#     "MealPrepSunday"      # Meal prep ideas and pics
# ]
# subreddits = [
#     "recipes",              # General recipe sharing
#     "AskCulinary",          # Cooking advice from chefs and enthusiasts
#     "BudgetFood",           # Extremely affordable cooking
#     "CastIron",             # Cooking and caring for cast iron cookware
#     "foodvideos",           # Recipes and food prep in video form
#     "fermentation",         # Sauerkraut, kimchi, kombucha, etc.
#     "Breadit",              # All things bread making
#     "slowcooking",          # Crockpot and slow cooker recipes
#     "instapot",             # Instant Pot recipes and tips
#     "pasta"                 # Dishes, recipes, and pasta obsessions
# ]
# subreddits = [
#     "CulinaryPlating",       # Beautiful and creative food presentation
#     "EatCheapAndHealthy",    # Affordable and nutritious meals
#     "seriouseats",           # Community for the Serious Eats website
#     "TopSecretRecipes",      # Reverse-engineered brand-name recipes
#     "Baking",                # All things baking: bread, cakes, cookies, etc.
#     "Sourdough",             # Dedicated to sourdough baking
#     "BudgetFood",            # Meals on a strict budget
#     "PlantBasedDiet",        # Whole food, plant-based diet ideas
#     "WhatIsThisFood",        # Identify unknown foods and ingredients
#     "AskBaking"              # Q&A for baking-related issues and techniques
# ]
# subreddits = [
#     "ShowerOrange",
#     "BreadStapledToTrees",
#
#     "MenInPantries",
#     "AvocadosGoneWild",
#     "Treecipes",
#     "DrunkenCookery",
#     "BowlOfLemons",
#     "Fffffffuuuuuuuuuuuud",
#     "Random_Acts_Of_Pizza"
# ]

# subreddits = [
#     "AskFoodScience",
#     "BudgetMeals",
#     "TopOfTheFoodChain",
#     "FreezerCooking",
#     "FoodPhotography",
#
#     "FoodSafety",
#     "JustNoRecipes",
#     "GloriousFood",
#     "Tofu"
# ]
# subreddits = [
#     "CookingForBeginners",
#     "EasyCrockpot",
#     "HealthyEating",
#     "BudgetFriendlyMeals",
#     "MealPrepRecipes",
#     "QuickMeals",
#     "HomemadeFood",
#     "KitchenGadgets",
#     "FoodBudgeting",
#     "ZeroWasteCooking"
# ]
# subreddits = [
#     "MiddleEasternFood",
#     "LebaneseFood",
#     "AskMiddleEastern",
#     "PersianFood",
#     "HalalFood",
#     "ArabFood",
#     "SyrianFood",
#     "IsraeliFood",
#     "MaghrebCuisine",  # North African Arab cuisines
#     "ArmenianFood"     # Often overlaps with Levantine flavors
# ]
subreddits = [
    "CleaningTips",
    "CleanHome",
    "CleaningHack",
    "HowTo",
    "HomeImprovement",
    "OrganizedHome",
    "Frugal",
    "ZeroWaste",
    "Homeowners",
    "LifeProTips"
]


if __name__ == "__main__":
    print("🔧 Starting parallel subreddit crawling...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(crawl_subreddit, subreddits)
    print("\n🎉 All subreddits processed!")
