# Twitter Scraper Telegram Bot

The Twitter Scraper Telegram Bot is a Python-based bot developed to scrape tweets from influencers' Twitter accounts and send them via Telegram. This bot utilizes the `snscrape` library to fetch tweets and the Telegram Bot API to send the scraped tweets to specified Telegram channels, users, or forum topics.

## Features

- **Tweet Scraping**: The bot uses the `snscrape` library to scrape tweets from Twitter profiles of influencers.
- **Multi-User to Multi-Topic Mapping**: Configure different Twitter users to send tweets to different Telegram chats and specific forum topics.
- **Flexible Configuration**: You can easily configure the bot to scrape tweets from specific influencers, specify the number of tweets to fetch, and set the scraping frequency.
- **Telegram Integration**: The bot integrates with the Telegram Bot API to send the scraped tweets to specified Telegram channels, groups, or forum topics.
- **Forum Topic Support**: Send tweets to specific topics in Telegram forum groups using `message_thread_id`.
- **Customizable Message Formatting**: You can customize the format of the message that is sent to Telegram, including the tweet content, username, timestamp, and any additional information you require.
- **Error Handling**: The bot includes error handling to ensure smooth operation and notify you in case of any issues encountered during the scraping process.

## Installation

1. Clone the repository to your local machine:
```bash
git clone https://github.com/navtemmt/Twitter-Scraper-Telegram-Bot.git
```

2. Install the required dependencies using pip:
```bash
cd Twitter-Scraper-Telegram-Bot
pip install -r requirements.txt
```

3. Obtain Telegram Bot API credentials:
   - Create a new bot using the BotFather on Telegram to obtain the bot token.
   - Set the bot token in the `main.py` file (replace the `bot_token` variable).

4. Configure your Twitter users and Telegram destinations (see Configuration section below).

## Configuration

### Twitter Users Configuration

Edit `influencers.json` to specify which Twitter users to scrape:

```json
[
  "elonmusk",
  "naval",
  "balajis"
]
```

### Multi-User to Multi-Topic Mapping

The bot supports routing different Twitter users to different Telegram destinations using `mapping_config.json`. This allows you to:

- Send tweets from different Twitter users to different Telegram chats
- Send tweets to specific topics in Telegram forum groups
- Have a default destination for unmapped users

#### Example mapping_config.json

```json
{
  "mappings": {
    "elonmusk": {
      "chat_id": -1001234567890,
      "topic_id": 123
    },
    "naval": {
      "chat_id": -1001234567890,
      "topic_id": 456
    },
    "balajis": {
      "chat_id": -1009876543210,
      "topic_id": null
    }
  },
  "default": {
    "chat_id": -1001111111111,
    "topic_id": null
  }
}
```

#### Configuration Options

- **mappings**: Object containing user-specific routing configurations
  - **key**: Twitter username (without @)
  - **chat_id**: Telegram chat ID (negative for groups/channels)
  - **topic_id**: Forum topic ID (use `null` for regular groups/channels)

- **default**: Fallback configuration for unmapped Twitter users
  - **chat_id**: Default Telegram destination
  - **topic_id**: Default topic ID (`null` for no topic)

#### Setting Up Per-User Routing

1. **Get Chat IDs**: 
   - For channels: Forward a message from the channel to @userinfobot
   - For groups: Add @userinfobot to the group and use `/start`
   - Chat IDs for groups/channels are negative numbers

2. **Get Topic IDs** (for forum groups only):
   - Right-click on a topic in the forum group
   - Copy the link and extract the topic ID from the URL
   - Example: `https://t.me/c/1234567890/123/456` → topic ID is `456`

3. **Configure mappings**:
   - Create/edit `mapping_config.json` with your specific routing rules
   - Set `topic_id` to `null` for regular groups/channels
   - Set `topic_id` to a number for forum topics

### Other Configuration Files

- **`advertisement.json`**: Configure promotional messages to include with tweets
- **`templates.json`**: Set up message templates per chat
- **`admins.json`**: Define bot administrators and their permissions

## Usage

1. Configure all JSON files according to your needs:
   - `influencers.json`: List of Twitter usernames to monitor
   - `mapping_config.json`: Routing configuration for users and destinations
   - `advertisement.json`: Advertisement content (optional)

2. Start the bot:
```bash
python main.py
```

3. The bot will:
   - Start scraping tweets from configured Twitter users every 5 minutes
   - Route tweets to appropriate Telegram destinations based on mapping configuration
   - Send tweets to specific forum topics if configured
   - Include advertisements and custom formatting

**Note**: It is recommended to run the bot on a server or in the background to ensure continuous scraping and message delivery.

### Bot Commands

- `/start`: Initialize the bot (for authorized users only)
- Bot supports group selection for administrators

## File Structure

```
Twitter-Scraper-Telegram-Bot/
├── main.py                 # Main bot script
├── requirements.txt        # Python dependencies
├── influencers.json       # Twitter users to monitor
├── mapping_config.json    # User-to-destination routing
├── advertisement.json     # Advertisement content
├── templates.json         # Message templates
├── admins.json           # Bot administrators
├── message_ids.json      # Message tracking (auto-generated)
├── enabled_groups.json   # Enabled groups (auto-generated)
├── selected_groups.json  # Selected groups (auto-generated)
└── tweets-data.json      # Scraped tweet data (auto-generated)
```

## How It Works

1. **Scraping**: Every 5 minutes, the bot scrapes the latest tweets (up to 20 per user) from configured Twitter accounts
2. **Filtering**: Only tweets from the last 5 minutes are processed to avoid duplicates
3. **Routing**: Based on `mapping_config.json`, tweets are routed to appropriate Telegram destinations
4. **Forum Support**: If a `topic_id` is specified, tweets are sent to that specific forum topic
5. **Message Management**: Previous messages are deleted and replaced with new ones to keep chats clean
6. **Templates**: Custom message templates can be applied per destination

## Troubleshooting

- **Bot not receiving updates**: Check that the bot token is correct and the bot is started
- **Messages not appearing in forum topics**: Verify the `topic_id` is correct and the bot has permissions
- **Chat ID errors**: Ensure chat IDs are negative for groups/channels and the bot is added to the chat
- **Permission errors**: Make sure the bot has permission to send messages and manage messages in target chats

## Contributions

Contributions to the Twitter Scraper Telegram Bot are welcome! If you have any suggestions, bug reports, or feature requests, feel free to submit them as issues or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the code in accordance with the terms of the license.

## Acknowledgements

The Twitter Scraper Telegram Bot makes use of the following libraries:

- **[snscrape](https://github.com/JustAnotherArchivist/snscrape)** - A Python library for scraping social media websites (including Twitter).
- **[pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)** - A Python wrapper for the Telegram Bot API.
- **[schedule](https://github.com/dbader/schedule)** - Python job scheduling for humans.

Special thanks to the developers of these libraries for their contributions.
