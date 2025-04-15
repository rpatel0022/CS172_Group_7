# Reddit Crawler

## Setup Instructions

Follow these steps to set up the project and run the Reddit crawler script.

### 1. **Clone the Repository**
Clone the repository to your local machine:
```bash
git clone https://github.com/rpatel0022/CS172_Group_7.git
```

### 2. **Create Your `.env` File**
- Copy the `.env.template` file to `.env`.
- Open the `.env` file and fill in your **own Reddit API credentials**:
  - `client_id`: Your Reddit app's client ID.
  - `client_secret`: Your Reddit app's client secret.
  - `REDDIT_USERNAME`: Your Reddit username.
  - `REDDIT_PASSWORD`: Your Reddit password.

Your .env file should look like this:
``` bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### 3. **Install Dependencies**
pip3 install praw python-dotenv requests

### 4. **Run the Script**
python3 crawler.py


