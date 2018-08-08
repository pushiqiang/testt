

class AIBotRecord:
    _bots = {}

    @classmethod
    def add_bot(cls, key, bot_info):
        cls._bots[key] = bot_info
        return bot_info

    @classmethod
    def get_bot(cls, key):
        return cls._bots.get(key)

    @classmethod
    def all(cls):
        return cls._bots.values()

    @classmethod
    async def delete(cls, key):
        bot = cls._bots.get(key)
        if bot:
            await bot.ws_close()
            del bot

    @classmethod
    def count(cls):
        return len(cls._bots)
