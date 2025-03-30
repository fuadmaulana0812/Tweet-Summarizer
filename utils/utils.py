import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def read_user():
    """
    Reads Twitter account data from an Excel file, filters valid accounts, and extracts usernames.

    Returns:
        list: A list of Twitter usernames extracted from the "Twitter Account" column.
    """
    try:
        # Read the Excel file, skipping the first two rows
        logging.info("📂 Reading Twitter accounts from Excel file...")
        df = pd.read_excel('Twitter Accounts_DeSci AI Agent_210325.xlsx', skiprows=2)

        # Filter rows where "Twitter Account" starts with "https"
        df_filtered = df[df["Twitter Account"].astype(str).str.startswith("https")].copy()

        # Extract username from the "Twitter Account" URL
        df_filtered.loc[:, "Username"] = df_filtered["Twitter Account"].str.extract(r"https://x\.com/([^/]+)")

        # Convert the usernames to a list
        user_list = df_filtered["Username"].tolist()

        logging.info(f"✅ Successfully extracted {len(user_list)} usernames.")
        return user_list
    
    except FileNotFoundError:
        logging.error("❌ Excel file not found. Please ensure the file exists and the path is correct.")
        return []
    except Exception as e:
        logging.error(f"❌ An error occurred while reading Twitter accounts: {e}")
        return []

async def export_txt(formatted_tweets):
    """
    Exports the formatted tweets to the 'output_tweets.txt' file.

    Args:
        formatted_tweets (str): The formatted tweets to be written to the file.
    """
    try:
        logging.info("Exporting tweets to 'output_tweets.txt'.")
        with open("output_tweets.txt", "a", encoding="utf-8") as f:
            f.write("\n\n\n")
            f.write(formatted_tweets)
        logging.info("✅ Tweets exported successfully to 'output_tweets.txt'.")
    except Exception as e:
        logging.error(f"❌ An error occurred while exporting tweets: {e}")