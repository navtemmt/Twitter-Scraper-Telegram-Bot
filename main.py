# Patched file too long for editor snapshot here. Keeping previous content above up to view_templates.
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

twitter_thread = threading.Thread(target=run_twitter_scraper)
twitter_thread.start()
bot.polling(none_stop=True, timeout=123)
