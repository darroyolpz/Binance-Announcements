import logging, os, time, tweepy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import bs4 as bs
import urllib.request

# Create an environment variable and get the token
TG_TOKEN = os.environ.get('TG_TOKEN')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the tokens
consumer_key = os.environ.get('TW_CONSUMER_KEY')
consumer_secret = os.environ.get('TW_CONSUMER_SECRET')
access_token = os.environ.get('TW_ACCESS_TOKEN')
access_token_secret = os.environ.get('TW_ACCESS_TOKEN_SECRET')

# authentication of consumer key and secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

# authentication of access token and secret
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Binance extract function
def extract_binance(main_webpage, key_words):
	# Create an empty string to store matchings
	final_list = []

	# Scrap the entire web-page
	sauce = urllib.request.urlopen(main_webpage).read()
	soup = bs.BeautifulSoup(sauce, 'lxml')

	# Extract the announcements
	list = soup.find_all('li', class_ = 'article-list-item')

	# Check for matchings
	for article in list:
		article_text = article.get_text().replace('\n', '')

		for item in key_words:
			# If matching, create a new list. Use LOWERCASE!
			if item in article_text.lower():
				article_link = 'https://www.binance.com' + article.find('a').get('href')
				final_list.append([article_text, article_link])

	return final_list

# Telegram function
def tg_call(update, context):
	# Send a message when the command /start is triggered 
	update.message.reply_text("Hello mate! Let me start checking")

	# Create two empty list for storing and comparing urls
	old_urls, new_urls = [], []

	# Create a bag of key words for getting matches
	key_words = ['list', 'token sale', 'open trading', 'opens trading']

	# Create the first pass
	main_webpage = 'https://www.binance.com/en/support/categories/115000056351'
	old_urls = extract_binance(main_webpage, key_words)

	# Loop pass - Watchdog mode
	while True:
		# Get new list of urls
		new_urls = extract_binance(main_webpage, key_words)
		
		for item in new_urls:
			# Compare if they were included in the former list
			if item not in old_urls:
				msg = item[0] + '\n' + item[1]
				api.update_status(msg) # Twitter
				update.message.reply_text(msg) # Telegram

				# Append the message in order to not repeat the messages
				old_urls.append(item)

		update.message.reply_text('Done for now. Time to go to sleep mate!')
		time.sleep(900) # Sleep for 15 min

# Main function
def main():

	# Create the updater
	updater = Updater(TG_TOKEN, use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Start the loop with /start
	dp.add_handler(CommandHandler("start", tg_call))

	# Start the Bot
	updater.start_polling()
	updater.idle() # killall python3.7 to kill the app

# Start - Check if this file is run directly by python or it is imported
if __name__ == '__main__':
	main()