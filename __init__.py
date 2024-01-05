import os
import sys
import re
import pprint as pp

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# This pattern matches any string starting with an '@'.
usr_ptrn = re.compile('@[\S]*')

# Initializes app with a bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# In order to not get rate limited by Slack, we must dynamically fetch the id of the custom field we want manually.
# See https://api.slack.com/methods/users.profile.get#arg_include_labels
field_id = ""
for field in app.client.team_profile_get()['profile']['fields']:
    if field["label"] == "Kevlar":
        field_id = field["id"]


# Deletes the provided message in the provided channel
def deflect(channel, ts):
    app.client.chat_delete(channel=channel, ts=ts)

@app.event({
    "type": "message",
    # "subtype": "channel_join"
})
def detect_mention(event, say, body):
    # Messages of certain subtypes do not contain text, thus we need to terminate early
    if "text" not in body["event"]:
        return
    matches = usr_ptrn.findall(body["event"]["text"])
    if matches:
        say(f"{list(match.strip('@>') for match in matches)}")
    else:
        # Message does not "@" anyone, so ignore
        return

    mentions = list(match.strip('@>') for match in matches)
    for uid in mentions:
        try:
            if app.client.users_profile_get(user=uid)['profile']['fields'][field_id]['value'] == "true":
                # Kevlar is set, proceed to delete message
                deflect(channel=event["channel"], ts=event["ts"])
                say(f"User(s) {app.client.users_profile_get(user=uid)['profile']['display_name']} have Kevlar enabled and do not want to be sniped, message deleted.")
                break
                # say(f"{app.client.users_profile_get(user=uid)['profile']['fields'][field_id]['value']}")
        except KeyError:
            # Kevlar not set
            pass
    return


# Start your app
if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt as ki:
        sys.exit()
