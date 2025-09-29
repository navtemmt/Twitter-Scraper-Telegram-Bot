import json
import datetime
import threading
import pytz
import telebot
from telebot import types
import random
import snscrape.modules.twitter as sntwitter
from tqdm import tqdm
import schedule
import time
import os

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '6285308929:AAFHF1mwb83XXt2MJhTzosY17d-m1nVqHMo'

# File paths
enabled_groups_file = 'enabled_groups.json'
combined_config_file = 'combined_config.json'
templates_file = 'templates.json'
message_ids_file = 'message_ids.json'
admins_file = 'admins.json'

bot = telebot.TeleBot(bot_token)

# Helper functions for JSON operations
def _load_json(file_path, default=None):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return default or {}
    except (json.JSONDecodeError, IOError):
        return default or {}

def _save_json(file_path, data):
    """Save data to JSON file"""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except IOError as e:
        print(f"Error saving {file_path}: {e}")

def _safe_delete(file_path):
    """Safely delete file if exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass

# Load combined configuration
def load_combined_config():
    """Load Twitter user configuration with routing information"""
    return _load_json(combined_config_file, {
        "users": [],
        "default": {
            "chat_id": None,
            "topic_id": None
        }
    })

def load_admins():
    return _load_json(admins_file)

def load_enabled_groups():
    return _load_json(enabled_groups_file)

def load_templates():
    return _load_json(templates_file)

def load_message_ids():
    return _load_json(message_ids_file)

def load_selected_group():
    return _load_json('selected_groups.json')

def save_message_ids(message_ids):
    _save_json(message_ids_file, message_ids)

def get_saved_message_id(chat_id):
    message_ids = load_message_ids()
    return message_ids.get(str(chat_id))

def save_message_id(chat_id, message_id):
    message_ids = load_message_ids()
    message_ids[str(chat_id)] = message_id
    save_message_ids(message_ids)

def send_message_with_link(chat_id, message, topic_id=None):
    """Send message to chat/group with optional topic_id for forum groups"""
    # Delete previous message if exists
    message_id = get_saved_message_id(chat_id)
    if message_id:
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    
    # Prepare kwargs for bot.send_message
    send_kwargs = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    # Add message_thread_id if topic_id is provided
    if topic_id:
        send_kwargs['message_thread_id'] = topic_id
    
    # Send the new message
    try:
        sent_message = bot.send_message(**send_kwargs)
        # Save the message ID for future reference
        save_message_id(chat_id, sent_message.message_id)
        return sent_message.message_id
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        return None

def twitter_scraper():
    """Main Twitter scraping function using combined config"""
    # Load combined configuration
    combined_config = load_combined_config()
    users = combined_config.get('users', [])
    default_config = combined_config.get('default', {})
    
    if not users:
        print("No users configured in combined_config.json")
        return
    
    n_tweets = 20
    time_limit = datetime.datetime.now(pytz.utc) - datetime.timedelta(minutes=5)
    
    # Load advertisements
    try:
        with open('advertisement.json', 'r', encoding='utf-8-sig') as ads_file:
            ads_data = json.loads(ads_file.read())
        random_ad = random.choice(ads_data["adsList"])
    except:
        random_ad = {"text": "No ads available", "link": "#"}
    
    # Load templates
    templates = load_templates()
    
    all_tweets_data = {}
    
    # Scrape tweets for each user
    for user_config in users:
        username = user_config.get('username')
        if not username:
            continue
            
        tweets_data = []
        
        try:
            scraper = sntwitter.TwitterUserScraper(username)
            
            for i, tweet in tqdm(enumerate(scraper.get_items()), total=n_tweets):
                if tweet.date.replace(tzinfo=pytz.UTC) < time_limit:
                    break
                
                data = {
                    "id": tweet.id,
                    "url": tweet.url,
                    "username": username
                }
                
                tweets_data.append(data)
                if i + 1 >= n_tweets:
                    break
        except Exception as e:
            print(f"Error scraping tweets for {username}: {e}")
            continue
        
        if tweets_data:
            all_tweets_data[username] = {
                'tweets': tweets_data,
                'chat_id': user_config.get('chat_id'),
                'topic_id': user_config.get('topic_id')
            }
    
    # Save tweets data
    with open('tweets-data.json', "w") as json_file:
        json.dump(all_tweets_data, json_file)
    
    # Send tweets using user-specific routing
    if not all_tweets_data:
        print("No tweets available.")
        return
    
    print("Preparing Tweets...")
    
    # Process each Twitter user and send to their configured destination
    for username, user_data in all_tweets_data.items():
        tweets = user_data['tweets']
        chat_id = user_data['chat_id']
        topic_id = user_data['topic_id']
        
        if not tweets:
            continue
        
        # Use default config if user doesn't have specific routing
        if not chat_id:
            if default_config.get('chat_id'):
                chat_id = default_config['chat_id']
                topic_id = default_config['topic_id']
            else:
                print(f"No chat_id configured for {username} and no default config")
                continue
        
        # Get template for this chat
        chat_id_str = str(chat_id)
        template_text = ""
        if chat_id_str in templates:
            template_text = templates[chat_id_str].get("template_text", "")
        
        # Build message content
        ad_message = f"Ad: [{random_ad['text']}]({random_ad['link']})"
        title = f"🚀 Tweets from @{username}\n\n"
        message = ""
        
        # Add tweet links
        for tweet_data in tweets:
            if 'id' in tweet_data and 'username' in tweet_data:
                url = "https://twitter.com/intent/tweet?text=" + str(template_text) + "&in_reply_to=" + str(tweet_data['id'])
                username_display = tweet_data['username']
                message += f"[{username_display}]({url}) || "
        
        message = message.rstrip(" || ")
        
        if not message:
            print(f"No tweet links generated for {username}")
            continue
        
        combined_message = title + message + '\n\n' + ad_message
        
        print(f"Sending tweets for {username} to {chat_id} (topic: {topic_id})")
        print(combined_message)
        
        # Send message with topic support
        send_message_with_link(chat_id, combined_message, topic_id)

# Bot handlers (keeping existing functionality)
admins = load_admins()

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    username = message.from_user.username
    if message.chat.type == 'private':
        if username in admins:
            admin_details = admins[username]
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
            for group_id, group_details in admin_details.items():
                if group_id != 'group_name' and group_id != 'group_id':
                    group_name = group_details['group_name']
                    markup.add(telebot.types.KeyboardButton(group_name))
            bot.send_message(message.chat.id, 'Select a group:', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'You are not authorized to use this bot.')

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_group_selection(message):
    username = message.from_user.username
    selected_group_name = message.text
    if username in admins:
        admin_groups = admins[username]
        selected_group = None
        for group_id, group_details in admin_groups.items():
            if group_details.get('group_name') == selected_group_name:
                selected_group = {'group_name': group_details['group_name'], 'group_id': group_id}
                break
        if selected_group:
            sg = load_selected_group()
            sg[username] = selected_group
            _save_json('selected_groups.json', sg)
            bot.send_message(message.chat.id, f"Success! Selected group: {selected_group['group_name']}")
        else:
            bot.send_message(message.chat.id, 'Invalid group selection.')
    else:
        bot.send_message(message.chat.id, 'You are not authorized to use this bot.')

# Scheduler
def run_twitter_scraper():
    schedule.every(5).minutes.do(twitter_scraper)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start
print("Starting Twitter Scraper Bot with combined user configuration...")
twitter_thread = threading.Thread(target=run_twitter_scraper)
twitter_thread.start()
bot.polling(none_stop=True, timeout=123)
