import re

from cardinal.decorators import event, regex

PROMPT_REGEX = r"^(.*) \(\d\) \(cash \$\d+\) on .*$"
GAME_OVER_REGEX = r"^Then (.+) WINS!!!!!$"
GAME_NICK = "monop"
GAME_CHANNEL = "#monop"


class MonopNotifierPlugin:
    def __init__(self, cardinal):
        self.db = cardinal.get_db('monop_notifier', default={
            'current_prompt': None,
        })

    @regex(PROMPT_REGEX)
    def find_prompt(self, cardinal, user, channel, message):
        if user.nick != GAME_NICK:
            return

        if channel != GAME_CHANNEL:
            return

        match = re.match(PROMPT_REGEX, message)

        with self.db() as db:
            db['current_prompt'] = {
                'nick': match.group(1),
                'prompt': message,
            }

    @regex(GAME_OVER_REGEX)
    def game_over(self, cardinal, user, channel, message):
        if user.nick != GAME_NICK:
            return

        if channel != GAME_CHANNEL:
            return

        with self.db() as db:
            db['current_prompt'] = None

    @event("irc.join")
    def on_join(self, cardinal, user, channel):
        if channel != GAME_CHANNEL:
            return

        with self.db() as db:
            prompt = db['current_prompt']

        if not prompt:
            return

        if user.nick.lower() != prompt['nick'].lower():
            return

        cardinal.sendMsg(channel, prompt['prompt'])
        cardinal.sendMsg(channel, "-- Command:")


entrypoint = MonopNotifierPlugin
