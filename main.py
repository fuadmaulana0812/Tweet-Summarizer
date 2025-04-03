import asyncio
import schedule
from scraper.selenium_scraper import TwitterSelenium
from summarizer.summarize_tweets_openai import process_tweets
from utils.telegram import Telegram
from utils.utils import read_user
import logging
import time
from datetime import datetime, timedelta, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def job():
    """
    The main scheduled task that performs the following steps:
    1. Reads Twitter accounts from the excel file.
    2. Scrapes tweets using Selenium.
    3. Processes tweets using OpenAI's language model.
    4. Posts the processed tweets as a thread on Twitter.
    5. Sends the processed tweets to a Telegram group.

    Returns:
        None
    """
    logging.info("🔄 Running Scheduled Task...")

    # ✅ Get current time 
    time_loc = timezone(timedelta(hours=-5))
    end_datetime = datetime.now(time_loc)
    start_datetime = end_datetime - timedelta(hours=4)
    logging.info(f"Processing tweets from {start_datetime} to {end_datetime}.")
    
    try:
        # ✅ Read Twitter accounts from Excel file
        user_list = await read_user()

        # ✅ Initialize Selenium Scraper
        selenium_scraper = TwitterSelenium(start_datetime, end_datetime)
        selenium_scraper.setup_driver()

        if selenium_scraper.login():
            # ✅ Scrape tweets
            tweets_data = await selenium_scraper.scrape_tweets(user_list)

            # ✅ Process tweets (Assuming `process_tweets` is an async function)
            formatted_tweets = await process_tweets(tweets_data, start_datetime, end_datetime)
            print(formatted_tweets)

            # # ✅ Post a Twitter thread
            await selenium_scraper.post_tweet(formatted_tweets)

            # # ✅ Post to Telegram channel
            telegram = Telegram()
            await telegram.send_telegram_message(formatted_tweets)

        selenium_scraper.driver.quit()  # Close browser
        logging.info("✅ Scheduled task completed successfully.")

    except Exception as e:
        logging.error(f"❌ An error occurred during the scheduled task: {e}")

# asyncio.run(job())

# ✅ Schedule the job at specific times (every 4 hours)
schedule.every().day.at("05:00").do(lambda: asyncio.run(job()))
schedule.every().day.at("09:00").do(lambda: asyncio.run(job()))
schedule.every().day.at("13:00").do(lambda: asyncio.run(job()))
schedule.every().day.at("17:00").do(lambda: asyncio.run(job()))
schedule.every().day.at("21:00").do(lambda: asyncio.run(job()))
schedule.every().day.at("01:00").do(lambda: asyncio.run(job()))

logging.info("🕒 Scheduler started! Running job every 4 hours...")

# ✅ Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)  # Prevent high CPU usage