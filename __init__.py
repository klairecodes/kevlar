import os
import sys
import re
import pprint as pp

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import psycopg

# This pattern matches any string starting with an '@'.
usr_ptrn = re.compile('@[\S]*')

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# In order to not get rate limited by Slack, we must fetch the id of the custom field we want manually.
# See https://api.slack.com/methods/users.profile.get#arg_include_labels
field_id = ""
for field in app.client.team_profile_get()['profile']['fields']:
    if field["label"] == "Kevlar":
        field_id = field["id"]

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
    matches = usr_ptrn.findall(body["event"]["text"])
    if matches:
        say(f"{list(match.strip('@>') for match in matches)}")
    else:
        say("No matches.")

    mentions = list(match.strip('@>') for match in matches)
    # say(f"{mentions[0]}")
    # pp.pp(f"{app.client.team_profile_get()['profile']['fields']}")

    # pp.pp(f"{app.client.team_profile_get()}", depth=1, width=20)
    # say(f"{app.client.users_profile_get(user=mentions[0])}")
    for uid in mentions:
        try:
            if app.client.users_profile_get(user=uid)['profile']['fields'][field_id]['value'] == "true":
                # Kevlar is set, proceed to delete message
                pass
            say(f"{app.client.users_profile_get(user=uid)['profile']['fields'][field_id]['value']}") 
        except KeyError:
            # Kevlar not set
            pass


# Start your app
if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt:
        sys.exit()

