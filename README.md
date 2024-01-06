# Kevlar
Kevlar is a Slack bot that prevents a user from being added to a channel on an opt-in basis.

## How it works
When the Kevlar bot is added to a channel, it listens to two events: messages and users joining a channel.  

When a message event happens, it checks the message for if any users were mentioned via `@<user>`, and query's each user's Kevlar custom field. If any user has their field set to true, Kevlar deletes the message and notifies the channel with a message that it did so with the specific user(s) that had Kevlar enabled.  

When a user joins the channel, whether through being mentioned or being added, Kevlar query's that user's Kevlar custom field. If it is set to true, Kevlar leaves the `was added to #<channel> by <user>.` message alone, removes the user from the channel, and notifies the channel with a message that it did so.

## Requirements
- Python version >= `python 3.11.6`
- A Python virtual environment
- The contents of [requirements.txt](requirements.txt) installed
- Docker/Podman if developing/deploying via container
- Slack
    - A Slack workspace
        - A Custom Field on a profile with the label "Kevlar" in the About Me section 
            - Follow [Slack's Administrator Docs](https://slack.com/help/articles/212281478-Customize-member-profiles) for how to get to the admin page.
            - At the configure profile page, scroll to the bottom for the "About me" section. Click `+Add data element`.
                - Label: Kevlar
                - Placeholder text: (optional)
                - Shows up in search: off
                - Data Source: Selectable options
                    - Selectable Options: false, true
                - Click `Save Changes`.
            - Click `Publish Changes`.
    - A Slack Bot
        - Following Slack's [Getting started with Bolt for Python](https://slack.dev/bolt-python/tutorial/getting-started) guide is advisable.
        - Socket Mode enabled
            - This can be done at `https://app.slack.com/app-settings/<your-workspace-id>/<your-app-id>/socket-mode`
        - Two Slack event Subscriptions (this adds their required scopes automatically)
            - This page is found at `https://api.slack.com/apps/<your-app-id>/event-subscriptions?`
            - Enable Events
            - Click `Subscribe to bot events` and add the following:
                - `member_joined_channel`
                - `message.channels`
                - `message.groups`
                - `message.im`
                - `message.mpim`
        - User and App token Scopes
            - A user bot token (starts with `xoxp-`, typically longer than nonuser) with the following OAuth Scopes:
                - `channels:history`
                - `channels:manage`
                - `channels:read`
                - `chat:write`
                - `groups_history`
                - `groups:read`
                - `groups_write`
                - `im:history`
                - `im:write`
                - `mpim:history`
                - `mpim:read`
                - `mpim:write`
                - `users.profile:read`
                - `users:read`
            - A Slack app token (starts with `xapp-`)with the following OAuth Scopes:
                - `channels:history`
                - `channels:read`
                - `channels:write`
                - `chat:write`
                - `groups:read`
                - `groups:write`
                - `im:write`
                - `mpim:read`
                - `mpim:write`
                - `users.profile:read`
            - If any of these are missing, Kevlar will complain in `stdout` and tell you which scope was required for the failed API call.
            - If any of these are redundant (not the minimum required) please let me know by creating an Issue!
        - A user service account with administrator privileges. This will be the account the bot acts as.

## Development
### Locally (Linux, Bash/Zsh)
- From the project's root:
- Create a Python virtual environment
```bash
python3 -m venv .venv
```
- Activate your virtual environment
```bash
source ./.venv/bin/activate
```
- Install dependencies
```bash
pip install -r requirements.txt
```
- Create a Slack app with the requirements mentioned above under Slack.
- Set the following environment variables to the tokens you created in your Slack Application:
    - These can be found under `OAuth&Permissions -> OAuth Tokens for Your Workspace`
```bash
export SLACK_APP_TOKEN=<your-app-token>
export SLACK_BOT_TOKEN=<your-bot-token>
```
- Run with
```
python3 app.py
```
- You should see `⚡️ Bolt app is running!` if setup was successful.
- Add your bot to the Slack channels/conversations that you would like it to be active in.
- Set a User's About me -> Kevlar field to different values for testing.
    - Note: This field is only visible in **web and desktop** profile settings as of writing. Accessed by clicking your profile at the bottom-left of the page.

### Docker/Podman (recommended)
- Coming soon!
