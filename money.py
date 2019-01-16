"""A module that can handle money."""
import json
from random import randint
from discord.ext.commands import group
import discord as d

from localize import _
import localize
from util import m2m

class Money:
    def __init__(self):
        self._mdict={}

    @group()
    async def money(self, ctx):
        pass

    def getum(self, uid):
        uid=str(uid)
        with open("money.json",encoding="utf-8") as f:
            self._mdict=json.load(f)
        return int(self._mdict.get(uid,0))

    def setum(self, uid, to):
        uid=str(uid)
        self._mdict[uid]=int(to)
        with open("money.json","w",encoding="utf-8") as f:
            json.dump(self._mdict, f)

    @staticmethod
    async def valid(ctx, uid, k):
        try:
            k=float(k)
            assert k>0 and int(k)==k
            return int(k)
        except:
            await ctx.send(_("money.num",uid))
            raise Exception

    @money.command()
    async def wallet(self, ctx):
        """財布を見る"""
        uid=str(ctx.author.id)
        m=self.getum(uid)
        embed=d.Embed(title=_("money.wallet.title",uid),
                      description=_("money.wallet.description",uid,m),
                      color=0xff4400)
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(embed=embed)

    @money.command()
    async def give(self, ctx, mention, k):
        """"お金をあげる"""
        uid=str(ctx.author.id)
        mntn=m2m(mention, ctx)
        if mntn.bot:
            await ctx.send(_("money.bot", uid))
            return
        try:
            k=await self.valid(ctx, uid,k)
        except:
            return
        muid=str(mntn.id)
        if not mntn or (mntn==ctx.author and muid!='398412979067944961'):
            await ctx.send(_("money.give.author", uid))
            return
        limit=not (uid == '398412979067944961' or ctx.author.permissions_in(ctx.message.channel).administrator)
        if limit:
            m=self.getum(uid)
            if k>m:
                await ctx.send(_("money.over",uid))
                return
            m-=k
            self.setum(uid, m)

        mm=self.getum(muid)
        mm+=k
        self.setum(muid, mm)
        await ctx.send(_("money.give.success",uid))

    @money.command()
    async def bet(self, ctx, k):
        """ギャンブルです。1回50K"""
        uid=str(ctx.author.id)
        try:
            k=await self.valid(ctx, uid,k)
        except Exception as e:
            print(e)
            return
        m=self.getum(uid)
        if k>m+50:
            await ctx.send(_("money.over",uid))
            return
        m-=50
        m-=k
        rate=randint(70,130)/100
        k*=rate
        self.setum(uid, int(m+k))
        await ctx.send(_("money.bet.done",uid))
