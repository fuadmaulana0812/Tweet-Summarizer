# Tweet Summarizer

## Objective

This project collects recent posts from a configured list of X accounts, summarizes each post with an OpenAI language model, and distributes the resulting digest to X and a Telegram chat. A scheduled job runs every four hours, making it useful for following updates across a set of DeSci and life-sciences accounts.

The workflow is intended to answer questions such as:

- What have the configured accounts posted during the latest collection window?
- Which updates are worth reviewing without reading every post in full?
- How can a concise digest be shared across social and messaging channels?

## Features

- Read account usernames, display names, and profile URLs from `user.json`.
- Log in to X with Selenium and collect posts from a recent time window.
- Avoid duplicate post URLs across the accounts processed in one run.
- Summarize each collected post with a configured OpenAI model.
- Include the account name and original post link in the generated digest.
- Publish the digest to X and send it to a Telegram chat.
- Run the workflow on a daily schedule at six four-hour intervals.
- Package the application and its browser dependencies with Docker.

## Workflow

The scheduled task reads the account list, opens a headless Chromium browser, logs in to X, and visits each configured profile. Posts with timestamps inside the previous four hours are passed to the summarizer. The formatted digest is then submitted to X and Telegram.

The account list is user-configurable. Each entry in `user.json` should have this shape:

```json
{
  "username": "example_account",
  "display_name": "Example Account",
  "user_link": "https://x.com/example_account"
}
```

The checked-in `user.json` contains a DeSci-focused example list. Update it to follow different public accounts.

## Summaries and delivery

Each post is summarized independently using LangChain's `ChatOpenAI` integration. The output includes a time-window heading, the account display name, a short summary, and the original post URL. If no posts are found in the window, the digest reports that there are no new updates.

The same formatted digest is sent to both destinations:

- **X:** posted through the authenticated Selenium browser session.
- **Telegram:** sent through the Telegram Bot API to the configured chat.

This is an automated publishing workflow. Review the generated summary and destination account configuration before enabling scheduled posting.

## Configuration

Create a `.env` file in the project root with the values required by `config/settings.py`:

```dotenv
API_KEY=your_application_api_key
TWITTER_USERNAME=your_x_username
TWITTER_EMAIL=your_x_account_email
TWITTER_PASSWORD=your_x_password
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_available_model_name
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_GROUP_ID=your_telegram_chat_id
```

`API_KEY` is declared as a required setting in the current application configuration. Store secrets in `.env` and do not commit that file. The repository's `.gitignore` already excludes `.env`.

## Run locally

Use Python 3.11, which is also the base version used by the Dockerfile. Selenium is configured for Chromium and ChromeDriver at `/usr/bin/chromium` and `/usr/local/bin/chromedriver`, respectively; the current driver setup therefore expects a Linux environment with those paths.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

After creating `.env` and configuring `user.json`, start the scheduler:

```bash
python main.py
```

The scheduler runs at **01:00, 05:00, 09:00, 13:00, 17:00, and 21:00** according to the machine's local timezone. Each run processes the previous four hours. Keep the process running for scheduled jobs to execute. The timestamps used for the collection window are currently set to UTC−05:00 in the source code.

## Run with Docker

Build and run the image from the project directory:

```bash
docker build -t tweet-summarizer .
docker run --env-file .env tweet-summarizer
```

The Dockerfile installs Chromium and a fixed ChromeDriver release. Browser compatibility may require updating those pinned versions if the X site or browser environment changes.

## Project structure

```text
main.py                              Scheduled collection and publishing workflow
config/settings.py                   Environment-based application settings
scraper/selenium_scraper.py          X login, post collection, and X publishing
summarizer/summarize_tweets_openai.py OpenAI-backed per-post summarization
utils/telegram.py                    Telegram Bot API delivery
utils/utils.py                       Account-list loading and text export helper
user.json                            Configured X accounts
requirements.txt                     Python dependencies
Dockerfile                           Container and browser setup
```

## Limitations and next steps

This is a portfolio automation project that relies on browser automation and the current structure of X pages. Login flows, page markup, rate limits, or platform policies can change and interrupt collection or posting. Scraping may miss posts that are not loaded in the profile page, and the four-hour collection window can leave gaps if the scheduler is stopped. OpenAI summaries can omit nuance or misstate details, so readers should use the linked original posts as the source of truth. The current application does not include retries, persistent run history, or delivery confirmation beyond logging.
