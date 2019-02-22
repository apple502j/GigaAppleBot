import builtins
import re
import traceback
import requests
import discord as d
from discord.ext import commands as c

def m2m(mention, ctx):
    mention=int(re.sub("[^0-9]","",mention))
    guild=ctx.guild
    return guild.get_member(mention)

def stream(fileobj, path, *opts):
    req = requests.get(path.format(*opts), stream=True)
    for block in req.iter_content(1024):
        fileobj.write(block)

def isonline(user):
    return user.status != d.Status.offline

def sortstr(string):
    arrs=string.split(" ")
    newarr=[]
    for word in arrs:
        newarr.append(''.join(sorted(word)))
    return ' '.join(newarr)

class SafeList(builtins.list):
    def __init__(self, *args):
        if len(args) == 1:
            try:
                super().__init__(args[0])
            except TypeError:
                super().__init__(args)
        else:
            super().__init__(args)

    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default

class RealMemberConverter(c.Converter):
    async def convert(self, ctx, arg):
        try:
            arg=arg.strip()
            print(f"Got {arg}")
            # yeah, it's on guild!
            maybe_id='0'
            if re.match("[0-9]+$", arg):
                maybe_id=arg
                print(f"{arg}: handled as ID {maybe_id}")
            else:
                groupy=re.match("<?@!?([0-9]+)>?$", arg)
                if groupy:
                    maybe_id=groupy.group(1)
                    print(f"{arg}: handled as mention {maybe_id}")
            if hasattr(ctx, 'guild') and ctx.guild:
                maybe_member_obj=ctx.guild.get_member(int(maybe_id))
                if maybe_member_obj:
                    print(f"{arg}: ID existed {maybe_member_obj}")
                    return maybe_member_obj
                else:
                    # some name people with number
                    print(f"{arg}: handled as name")
                    maybe_member_obj=ctx.guild.get_member_named(arg)
                    if maybe_member_obj:
                        print(f"{arg}: name existed {maybe_member_obj}")
                        return maybe_member_obj
                    else:
                        # second step
                        print(f"{arg}: second step")
            else:
                print("DMed")
            if maybe_id:
                print(f"ID search {arg}")
                for member in ctx.bot.get_all_members():
                    if member.id == int(maybe_id) and member.guild.get_member(ctx.author.id):
                        print(f"{arg}: ID searched, {member}")
                        return member

            if arg:
                nodisc=re.match("(.+)#[0-9]{4}$", arg)
                if nodisc:
                    arg=nodisc.group(1)
                print(f"Final search: {arg}")
                for guild in ctx.bot.guilds:
                    if guild.get_member(ctx.author.id):
                        for member in guild.members:
                            if member.name == arg or getattr(member, 'nick', None) == arg:
                                print(f"{arg}: guild searched, {member}")
                                return member
            return None
        except BaseException:
            traceback.print_exc()
