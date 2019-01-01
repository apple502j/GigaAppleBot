import re
import discord as d

def m2m(mention, ctx):
    mention=int(re.sub("[^0-9]","",mention))
    guild=ctx.message.channel.guild
    return d.utils.get(guild.members, id=mention)
