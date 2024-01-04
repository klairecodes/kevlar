import os
import sys
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import psycopg

# This pattern matches any string starting with an '@'.
usr_ptrn = re.compile('@[\S]*')

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    # say(f"Hey there <@{message['user']}>!")
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

@app.event({
    "type": "message",
    # "subtype": "channel_join"
})
def detect_mention(event, say, body):
    say(f'{body["event"]["text"]}')
    matches = usr_ptrn.findall(body["event"]["text"])
    if matches:
        say(f"{list(match.strip('@') for match in matches)}")
    else:
        say("No matches.")

    mentions = list(match.strip('@') for match in matches)


# Start your app
if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt:
        sys.exit()

