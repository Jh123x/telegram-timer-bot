# Telegram live timer bot

# What is it
This is a telegram bot that allows the user to have a "live" countdown on the event that they want to have.


# Quick start
1. Download this repository
2. Install the dependencies using `python -m pip install -r requirements.txt`
3. Create a `.env` file with the template [here](#creating-your-env-file)
4. Start the application by running `python Bot` at the root directory.


# Creating your `.env` file
```
API_ID=<Your API ID>
API_HASH=<Your API Hash>
BOT_TOKEN=<Your Bot Token>
```
1. Copy the template above (Note that there is no space between the `=` and the id itself)
2. Get your `API_ID` and `API_HASH` [here](https://my.telegram.org/apps/create)
3. Get your `BOT_TOKEN` from `@botfather` [here](https://core.telegram.org/bots)


# Note:
1. Note that once you turn off the bot, all the event information is lost. (This might be a feature to be added in the future)


# Contributing to the Project

Feel free to send in a pull request.

# Using the project

To Use this project, please add this line into your readme.
```markdown
Referenced from [Jh123x Timer bot](https://github.com/Jh123x/telegram-timer-bot)
```

# Tech Stack
[pyrogram](https://docs.pyrogram.org/)