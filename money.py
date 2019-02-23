"""A module that can handle money."""
import json
from random import randint
from discord.ext.commands import group, guild_only
import discord as d

from localize import _
import localize
from util import m2m, isonline

class Money:
    def __init__(self, bot, mtj):
        self._mdict={}
        self.bot=bot
        self.mtj=mtj

    @group()
    async def money(self, ctx):
        pass

    def getum(self, uid):
        uid=str(uid)
        with open("./settings/money.json",encoding="utf-8") as f:
            self._mdict=json.load(f)
        return int(self._mdict.get(uid,0))

    def setum(self, uid, to):
        uid=str(uid)
        self._mdict[uid]=int(to)
        with open("./settings/money.json","w",encoding="utf-8") as f:
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

    @guild_only()
    @money.command()
    async def give(self, ctx, mention, k):
        """"お金をあげる"""
        uid=str(ctx.author.id)
        mntn=m2m(mention, ctx)
        if not mntn:
            await ctx.send(_("money.give.maybeTransfer", uid))
            return
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
        limit=not (uid == '398412979067944961' or ctx.author.permissions_in(ctx.channel).administrator)
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

    @money.command()
    async def rate(self, ctx):
        """為替のレート"""
        global MONEY_EXCHANGE
        uid=str(ctx.author.id)
        s=""
        for k in MONEY_EXCHANGE:
            mntn="<@{0}>".format(MONEY_EXCHANGE[k]["id"])
            s+="{0}: 1ABK={1}{2}\n".format(mntn, MONEY_EXCHANGE[k]["rate"], k)
        await ctx.send(_("money.rate.rate", uid, s))

    @money.command()
    async def transfer(self, ctx, newbot, k):
        """Kを転送します"""
        MONEY_EXCHANGE=self.mtj["available"]
        uid=str(ctx.author.id)
        if newbot not in MONEY_EXCHANGE.keys():
            await ctx.send(_("money.transfer.unknownbot", uid, _("bot.sep", uid).join(
            list(MONEY_EXCHANGE.keys())
            )))
            return
        try:
            k=await self.valid(ctx, uid, k)
        except:
            return
        user_k=self.getum(uid)
        if user_k < k:
            await ctx.send(_("money.over",uid))
            return
        if not self.bot.get_channel(MONEY_EXCHANGE[newbot]["channel"]):
            await ctx.send(_("money.transfer.error", uid, "INVALID_CH"))
            return
        if not isonline(self.bot.get_channel(MONEY_EXCHANGE[newbot]["channel"]).guild.get_member(MONEY_EXCHANGE[newbot]["id"])):
            await ctx.send(_("money.transfer.sleeping", uid))
            return

        self.setum(uid, user_k-k)
        channel = self.bot.get_channel(MONEY_EXCHANGE[newbot]["channel"])
        rated_k=str(k*MONEY_EXCHANGE[newbot]["rate"])
        await channel.send(embed=d.Embed(title=uid, description=rated_k))
        await ctx.send(_("money.transfer.sent", uid))
