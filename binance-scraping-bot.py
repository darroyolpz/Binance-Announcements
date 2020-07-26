import os, requests
import pandas as pd
from bs4 import BeautifulSoup
from requests import get
from discord_webhook import DiscordWebhook

# Webhook settings
url_wb = os.environ.get('DISCORD_WH')

# Data for the scrap
url = "https://www.binance.com/en/support/announcement"
response = get(url)
soup = BeautifulSoup(response.text, 'html.parser')
news_list = soup.find_all(class_ = 'css-sbrje5')

# Create a bag of key words for getting matches
key_words = ['list', 'token sale', 'open trading', 'opens trading', 'perpetual']

# Open old database file
path = "C:/Users/d645daar/Documents/Codes/Binance Announcements/db.xlsx"
df = pd.read_excel(path)

# Empty list
updated_list = []

for news in news_list:
	article_text = news.text

	# Check for matchings
	for item in key_words:
		if (item in article_text.lower()) and (article_text not in df.values):
			article_link = 'https://www.binance.com' + news.get('href')
			msg = article_text + '\n' + article_link
			updated_list.append([article_text, article_link])
			print(article_text)

			# Send message to Discord server
			webhook = DiscordWebhook(url=url_wb, content=msg)
			response = webhook.execute()

# Export updated news to Excel
cols = ['Text', 'Link']
df = df.append(pd.DataFrame(updated_list, columns=cols), ignore_index = True)
df.to_excel(path, index = False)