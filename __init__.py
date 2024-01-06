import os
import sys
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# This pattern matches any string starting with an '@'.
usr_ptrn = re.compile('@[\\S]*')

# Initializes app with a bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# In order to not get rate limited by Slack, we must dynamically fetch the id
# of the custom field we want manually.
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
    # Messages of certain subtypes do not contain text, need to terminate early
    if "text" not in body["event"]:
        return

    matches = usr_ptrn.findall(body["event"]["text"])
    if not matches:
        # Message does not "@" anyone, so ignore
        return

    mentions = list(match.strip('@>') for match in matches)
    kevlar_uids = []
    for uid in mentions:
        try:
            if app.client.users_profile_get(user=uid)['profile']['fields'][field_id]['value'] == "true":
                kevlar_uids.append(uid)
        except KeyError:
            # Kevlar not set
            pass

    if kevlar_uids:
        # Kevlar is set by at least one user
        kevlar_users = []
        for kuid in kevlar_uids:
            display_name = app.client.users_profile_get(user=kuid)['profile']['display_name']
            real_name = app.client.users_profile_get(user=kuid)['profile']['real_name']
            user_str = display_name or real_name  # real_name if not set
            kevlar_users.append(user_str)

        deflect(channel=event["channel"], ts=event["ts"])
        if len(kevlar_users) > 1:
            # Pretty printing
            users_str = ", ".join(kevlar_users[:-1]) + "* and *" + kevlar_users[-1]
            say(f"Users *{users_str}* have Kevlar enabled and do not want to be in #snipes. Message deleted.")
        else:
            say(f"User *{''.join(kevlar_users)}* has Kevlar enabled and does not want to be #snipes. Message deleted.")

    return


# Start your app
if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt as ki:
        sys.exit()
