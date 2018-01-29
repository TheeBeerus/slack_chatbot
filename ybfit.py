import os
import re
import time

from slackclient import SlackClient

import logging

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+)>(.*)"

logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%Y.%m.%d %H:%M:%S',
    format='[%(asctime)s][%(name)s][%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)
# logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)


class Bot(object):

    def __init__(self, starterbot_id, slack_client):
        self._starterbot_id = starterbot_id
        self._slack_client = slack_client

    def parse_bot_commands(self, slack_events):

        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """

        messages = [e for e in slack_events if e["type"] == "message"]
        messages = [e for e in messages if not "subtype" in e]
        logger.debug('Parsing message events : %s', messages)

        for message in messages:
            user_id, msg_txt = parse_direct_mention(message["text"])
            logger.debug('Retrieve user id = %s with message : %s', user_id, message)
            if user_id == self._starterbot_id:
                return msg_txt, message["channel"]

        return None, None

    def handle_command(self, command, channel):
        """
            Executes bot command if the command is known
        """
        # Default response is help text for the user
        default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

        # Finds and executes the given command, filling in response
        response = None
        # This is where you start to implement more commands!
        if command.startswith(EXAMPLE_COMMAND):
            response = "Sure...write some more code then I can do that!"

        # Sends the response back to the channel
        self._slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response
        )


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def main():
    token = os.environ.get('SLACK_BOT_TOKEN')
    token = 'xoxb-306089280870-tu2bRwPQ5MnGuUH6pHo9G8c4'
    logger.debug('Token : %s', token)
    slack_client = SlackClient(token)
    if slack_client.rtm_connect():
        logger.info('Starter Bot connected and running !')
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        bot = Bot(starterbot_id=starterbot_id, slack_client=slack_client)
        while True:
            command, channel = bot.parse_bot_commands(slack_client.rtm_read())
            if command:
                bot.handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        logger.info('Connection failed.')


if __name__ == "__main__":
    main()
