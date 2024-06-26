# Word Cloud Slack Bot

## Description

Generate word clouds with Slack messages

## Features

- Currently supports adding bot to channel and calling /wordcloud to generate based on post history. Use the `usernames` keyword to make a wordcloud of usernames based on posting frequency.

## ToDo

- Make bot DM you the image instead of posting to channel (maybe)
- allow custom permissions for DMs instead of just channel that the bot is added to
- parameters in slash command to allow for customizing the word cloud image/color/size etc.

## Installation

Take it for a spin at https://wordcloudbot.ezdoes.xyz/slack/install

1. Clone the repository
2. Set up the necessary environment variables:

    - SLACK_SIGNING_SECRET
    - SLACK_CLIENT_ID
    - SLACK_CLIENT_SECRET
    - DB_USER
    - DB_PASSWORD
    - BOT_BASE_URL
    - PORT

3. Use docker compose for quick deploy with postgres or run locally

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.