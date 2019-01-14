import re
import requests
import discord as d

def m2m(mention, ctx):
    mention=int(re.sub("[^0-9]","",mention))
    guild=ctx.message.channel.guild
    return d.utils.get(guild.members, id=mention)

def stream(fileobj, path, *opts):
    req = requests.get(path.format(*opts), stream=True)
    for block in req.iter_content(1024):
        fileobj.write(block)
