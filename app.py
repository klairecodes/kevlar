import os
import sys
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Regex
# Matches any string starting with an '@'.
usr_ptrn = re.compile('@[\\S]*')
# Matches the default "user added to channel" Slack message
usr_add_msg_ptrn = re.compile("was added to #\\w* by @?\\w* ?\\w*.")
# Matches the default "user has joined the channel" Slack message
usr_joined_msg_ptrn = re.compile("<*@?\\w*>* has joined the channel")

# Initializes app with a bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# In order to not get rate limited by Slack, we must dynamically fetch the id
# of the custom field we want manually.
# See https://api.slack.com/methods/users.profile.get#arg_include_labels
field_id = ""
for field in app.client.team_profile_get()['profile']['fields']:
    if field["label"] == "Kevlar":
        field_id = field["id"]


# Gets a string representation of a user, real_name if display_name not set.
def get_user_rep(uid):
    try:
        display_name = app.client.users_profile_get(user=uid)['profile']['display_name']
        real_name = app.client.users_profile_get(user=uid)['profile']['real_name']
    except KeyError:
        return "null"
    return display_name or real_name


# Deletes the provided message in the provided channel
def delete_message(channel, ts):
    app.client.chat_delete(channel=channel, ts=ts)


# Removes a provided user from the provided channel
def kick(user, channel):
    app.client.conversations_kick(user=user, channel=channel)


@app.event({
    "type": "member_joined_channel",
})
def detect_join(event, say):
    user = event["user"]
    channel_str = app.client.conversations_info(channel=event['channel'])['channel']['name']
    user_str = get_user_rep(user)
    kevlar_enabled = app.client.users_profile_get(user=user)['profile']['fields'][field_id]['value'] == "true"
    try:
        if kevlar_enabled:
            kick(user, event['channel'])
            say(f"User *{user_str}* has Kevlar enabled and does not want to be in #{channel_str}. User has been removed.")
    except KeyError:
        # Kevlar not set
        return


@app.event({
    "type": "message",
})
def detect_mention(event, say, body):
    # Messages of certain subtypes do not contain text, need to terminate early
    if "text" not in body["event"]:
        return

    matches = usr_ptrn.findall(body["event"]["text"])
    if not matches:
        # Message does not "@" anyone, so ignore
        return
    # The second case doesn't normally happen, checked just in case that is ever the message format
    if usr_joined_msg_ptrn.findall(body["event"]["text"]) or usr_add_msg_ptrn.findall(body["event"]["text"]):
        # Message is Slack's "was added to #channel by user.", ignore
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
            user_str = get_user_rep(kuid)
            kevlar_users.append(user_str)

        delete_message(channel=event["channel"], ts=event["ts"])
        channel_str = app.client.conversations_info(channel=event['channel'])['channel']['name']
        if len(kevlar_users) > 1:
            # Pretty printing
            users_str = ", ".join(kevlar_users[:-1]) + "* and *" + kevlar_users[-1]
            say(f"Users *{users_str}* have Kevlar enabled and do not want to be in #{channel_str}. Message deleted.")
        else:
            say(f"User *{''.join(kevlar_users)}* has Kevlar enabled and does not want to be in #{channel_str}. Message deleted.")

    return


# Start your app
if __name__ == "__main__":
    try:
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt as ki:
        sys.exit()
