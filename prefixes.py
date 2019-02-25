import json
import re
from discord.ext import commands as c
from util import CogHelper, not_found
from localize import _

DEFAULT_PREFIX="me:"

class PrefixError(ValueError):
    pass

class PrefixManager(CogHelper, name="Prefix"):
    def __init__(self, bot):
        print("PrefixManager has been initialized")
        self.bot=bot
        self.bot.command_prefix = self.get_prefix_command

    @c.group()
    async def prefix(self, ctx):
        print(f"Prefix-related {ctx.invoked_subcommand}")
        if not ctx.invoked_subcommand:
            await not_found(ctx)

    @staticmethod
    def open_prefix():
        with open("./settings/prefix.json", "r") as pf:
            pfdata = json.load(pf)
        return pfdata

    @staticmethod
    def save_prefix(data):
        with open("./settings/prefix.json", "w") as pf:
            json.dump(data, pf)

    @staticmethod
    def valid(p):
        return not re.search("[@#<>`*/\\ ]|^me:$", p)

    def get_prefix(self, uid):
        uid=str(uid)
        pfdata=self.open_prefix()
        if pfdata.get(uid, None):
            return (pfdata[uid], DEFAULT_PREFIX)
        else:
            return (DEFAULT_PREFIX,)

    async def get_prefix_command(self, bot, msg):
        return self.get_prefix(msg.author.id)

    def set_prefix(self, uid, new=None):
        uid=str(uid)
        if (new is not None) and not self.valid(new):
            raise PrefixError
        pfdata=self.open_prefix()
        pfdata[uid]=new
        self.save_prefix(pfdata)

    @prefix.command(name="get")
    async def prefix_get(self, ctx):
        uid=ctx.author.id
        await ctx.send(_("prefix.get", uid, self.get_prefix(uid)[0]))

    @prefix.command(name="set")
    async def prefix_set(self, ctx, new):
        uid=ctx.author.id
        try:
            self.set_prefix(uid, new)
            await ctx.send(_("prefix.set", uid, new))
        except PrefixError:
            await ctx.send(_("prefix.invalid", uid))

    @prefix.command()
    async def reset(self, ctx):
        uid=ctx.author.id
        self.set_prefix(uid, None)
        await ctx.send(_("prefix.reset", uid))

    @c.is_owner()
    @prefix.command()
    async def force_set(self, ctx, userid: int, new = None):
        try:
            self.set_prefix(userid, new)
            await ctx.send(_("prefix.force", ctx.author.id, userid, new))
        except PrefixError:
            await ctx.send(_("prefix.invalid", uid))
