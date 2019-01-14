"""A module that can handle regex."""

import re
from discord.ext.commands import group

from localize import _

class Regex:
    @group()
    async def regex(self, ctx):
        pass

    @staticmethod
    @regex.command()
    async def sub(ctx, ex='`[^a-z]`', s='Hello World', to=''):
        res=re.sub(ex[1:-1], to, s)
        if res:
            await ctx.send(res)
        else:
            await ctx.send(_("regex.empty", ctx.author.id))

    @staticmethod
    @regex.command()
    async def valid(ctx, ex='`Valid.?Regex`'):
        uid=ctx.author.id
        try:
            a=re.compile(ex[1:-1])
            await ctx.send(_("regex.valid", uid))
        except:
            await ctx.send(_("regex.invalid", uid))

    @staticmethod
    @regex.command()
    async def match(ctx, ex='`([a-zA-Z]*)`', s='apple502j'):
        uid=ctx.author.id
        try:
            await ctx.send(_("bot.sep", uid).join(filter(lambda a:a,re.findall(ex[1:-1], s))))
        except:
            await ctx.send(_("regex.empty", uid))
