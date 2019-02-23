from datetime import datetime # logger time
import sys
from random import randint, shuffle # random color
from random import choice as randchoice
from html import escape, unescape # parse html
import re
import os
import shutil
import hashlib
import traceback
import platform
import time # system timestamp
from urllib.parse import quote
import json # parse json value
import asyncio # await/async
import subprocess
import requests # internet requests
import github3 # GitHub
import bs4
import pypinyin
import scratchapi2 # scratch news
from discord.ext import commands as c # bot commands
import discord as d # discord main
import eqapi # earthquake
import emoji as emojy
import mw_api_client as mwc
from emojiflags import lookup as ec
from localize import _
import localize
from util import stream, sortstr, m2m
from xmlhelp import all_in_one as get_help_embed

env=platform.system()
pippy="{0} freeze".format("pip3" if env=="Windows" else "pip3.6")
sp=subprocess.Popen(pippy, shell=True, stdout=subprocess.PIPE)
print("Waiting for subprocess...")
sp.wait()
versions=sp.stdout.read().decode("utf-8").strip().split()
VERSION_DICT=[]
for item in versions:
    keys=item.split("==", 1)
    if keys[0] in ('discord.py', 'aiohttp', 'beautifulsoup4', 'certifi', 'chardet',
                   'cryptography', 'emoji', 'github3.py', 'lxml', 'mw-api-client',
                   'oauthlib', 'pypinyin', 'requests', 'requests-oauthlib',
                   'scratchapi2', 'tornado', 'urllib3', 'websockets'):
        VERSION_DICT.append((keys[0], keys[1]))

HASH_DICT=[]
for f in ('main', 'eqapi', 'localize', 'money', 'regex', 'util'):
    with open("{0}.py".format(f), "rb") as fobj:
        HASH_DICT.append((f, hashlib.md5(fobj.read()).hexdigest()))

with open("./settings/token.txt") as tkn:
    TOKEN=tkn.read().strip()
TRANSLATELIMIT = 0
SCRATCHLIMIT = 0
P2PLIMIT = 0
FORUMLIMIT = 0
GHLIMIT = 0
with open("./settings/money_transfer.json", "r") as mtj:
    MONEY_TRANSFER_INFO = json.load(mtj)
with open("longwords.json", "r") as lwj:
    LONG_WORDS = json.load(lwj)
localize.update()
localize.getlocale(0)
bot = c.Bot(command_prefix="me:", activity=d.Activity(name="me:help Icon by kazuta123",
                                                                    type=d.ActivityType.watching))

from money import Money
bot.add_cog(Money(bot=bot, mtj=MONEY_TRANSFER_INFO))
from regex import Regex
bot.add_cog(Regex())
from whatis import WhatIs
bot.add_cog(WhatIs(bot=bot))

def clear_synth():
    try:
        shutil.rmtree("synth")
    except:
        pass
    try:
        os.mkdir("synth")
    except:
        pass

clear_synth()

def catnese(word, uid):
    sp=re.findall("."*randint(2,4),word)
    for i in range(len(sp)):
        if randint(0,1):
            sp[i]=_("translate.meow1", uid)
        else:
            sp[i]=_("translate.meow2", uid)
    return ''.join(sp)

@bot.event
async def on_raw_reaction_add(ev):
    uid=ev.user_id
    cid=ev.channel_id
    emoji=ev.emoji
    msg_id=ev.message_id
    channel = bot.get_channel(cid)
    text = (await channel.get_message(msg_id)).content
    LANGS = {
        ":flag_eg:":"al",
        ":flag_cn:":"zh",
        ":flag_hk:":"zh-tw",
        ":flag_tw:":"zh-tw",
        ":flag_mo:":"zh-tw",
        ":flag_cz:":"cz",
        ":flag_nl:":"nl",
        ":flag_us:":"en",
        ":flag_gb:":"en",
        ":flag_fr:":"fr",
        ":flag_de:":"de",
        ":flag_gr:":"el",
        ":flag_hu:":"hu",
        ":flag_id:":"id",
        ":flag_jp:":"ja",
        ":flag_kr:":"ko",
        ":flag_pt:":"pt",
        ":flag_ru:":"ru"
        }
    for i in LANGS.keys():
        modi = i.replace(":","").replace("flag_","").upper()
        if emoji.name == ec(modi):
            lang=LANGS[i]
            await channel.send(scratchapi2.Translate().translate(lang, text))
            return
    if emoji.name == emojy.emojize(":cat_face:"):
        await channel.send(catnese(text, uid))
        return

@bot.event
async def on_message_edit(old, new):
    msg=new
    if not msg.author.bot:
        return
    if msg.channel.id not in MONEY_TRANSFER_INFO["watch"]:
        return
    if not new.embeds:
        return
    embed=new.embeds[0]
    author=msg.author
    try:
        uid=int(embed.title)
    except ValueError:
        return
    adds_k=int(embed.description)
    #if author.id == 479964847912648705: #GAB
    if True:
        Money(bot, MONEY_TRANSFER_INFO).setum(uid, Money(bot, MONEY_TRANSFER_INFO).getum(uid)+adds_k)

@bot.event
async def on_message(msg):
    """ 返事 """
    ctx = await bot.get_context(msg)
    if msg.author.bot == True:
        return
    if "<@"+str(bot.user.id)+">" in msg.content and getattr(ctx, 'command', None) != 'invite':
        reply = _("bot.reply", msg.author.id, msg.author.mention)
        await ctx.send(reply)
    if msg.channel.id == 497983550625153024:
        import jobs
        jobs.send(msg, bot)
    await bot.invoke(ctx)

class TestException(c.CommandError):
    pass

@bot.event
async def on_command_error(ctx, error):
    uid=ctx.author.id
    command=getattr(ctx.command, 'name', '')
    if not command:
        await ctx.send(_("excs.noCommand", uid))
        return
    async def report(name, *args, detail=False, more=None):
        await ctx.send(_("excs."+name, uid, command, *args))
        if detail:
            report_ch=bot.get_channel(543744092014772224)
            if not report_ch:
                raise Exception("Cannot report this error")
            if getattr(ctx, 'guild', None):
                where='guild {0} channel {1}, message {2}'.format(ctx.guild.id, ctx.channel.id, ctx.message.id)
            else:
                where='DM of the user, message {0}'.format(ctx.message.id)
            more_formatted='\n{0}'.format(more) if more else ''
            report_ch.send('`{0}` is occured at {1} by {2}{3}\n<!@{4}>'.format(error,where,ctx.author.id, more_formatted, bot.owner_id))
    if isinstance(error, SystemExit):
        pass
    elif isinstance(error, (requests.ConnectionError, requests.HTTPError)):
        await report("http")
    elif isinstance(error, TestException):
        await report("test")
    elif isinstance(error, c.NoPrivateMessage):
        await report("noDM")
    elif isinstance(error, c.CommandOnCooldown):
        await report("cooldown", round(error.retry_after))
    elif isinstance(error, c.NotOwner):
        await report("notOwner", getattr(bot.get_user(bot.owner_id), 'name', _("excs.unknownUser", uid)))
    elif isinstance(error, c.MissingPermissions):
        await report("missingPerms", _("bot.sep", uid).join(error.missing_perms))
    elif isinstance(error, c.BotMissingPermissions):
        await report("missingBotPerms", _("bot.sep", uid).join(error.missing_perms), ctx.guild.owner.mention if ctx.guild else '')
    elif isinstance(error, (mwc.excs.WikiError.ratelimited, mwc.excs.WikiError.readapidenied)):
        await report("fatal", detail=True, more="Rate Limited")
    elif isinstance(error, localize.NoTranslationError):
        await report("translation", detail=True, more="Rate Limited")


async def member_join_test(you):
    if you.guild.id != 497978199087775754:
        return
    else:
        await you.create_dm()
        dm=you.dm_channel
        await dm.send("ようこそ! 以下のルールを読んでください。")
        with open("./settings/rules.md", "r", encoding="utf-8") as rules:
            stack=[]
            prev_txt=''
            txt=''
            for l in rules:
                stack.append(l)
                prev_txt=txt
                txt=''.join(stack)
                if len(txt) > 1900:
                    await dm.send('```\n{0}\n```'.format(txt))
                    stack=[l]
                    prev_txt=''
                    txt=''
            if txt != '':
                await dm.send('```\n{0}\n```'.format(txt))

@bot.event
async def on_member_join(you):
    await member_join_test(you)

bot.remove_command('help')
@bot.command()
async def help(ctx, name='core'):
    """ヘルプです"""
    if True:
        await ctx.send(embed=get_help_embed(name))
    if False:
        await ctx.send(_("help.invalid", ctx.author.id))

@bot.command()
@c.is_owner()
async def run(ctx, cmd):
    cmd=cmd[1:-1]
    await ctx.send(eval(cmd))

@bot.command('eval')
@c.is_owner()
async def eval_(ctx, *, arg):
    """Execute Python code. Only available to owner."""
    try:
        await eval(arg, globals(), locals())
    except BaseException as e:
        try:
            eval(arg, globals(), locals())
        except BaseException as e:
            pass

@bot.command()
async def credits(ctx):
    uid=ctx.author.id
    embed=d.Embed(color=d.Color.orange())
    embed.add_field(name=_("credits.title", uid), value=_("credits.credits", uid), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    """Get status"""
    uid=ctx.author.id
    embed=d.Embed(title=_("status.title", uid), color=randint(0, 0xffffff))
    md5str="```\n"
    for item in HASH_DICT:
        md5str+="{0}: {1}\n".format(item[0], item[1])
    md5str+="```"
    embed.add_field(name=_("status.md5s", uid), value=md5str, inline=False)
    ver_str="```\n"
    for item in VERSION_DICT:
        ver_str+="{0}: {1}\n".format(item[0], item[1])
    ver_str+="```"
    embed.add_field(name=_("status.versions", uid), value=ver_str, inline=False)
    os_ver=platform.uname()
    embed.add_field(name=_("status.os", uid), value="{0[0]} {0[2]} ({0[3]})".format(os_ver), inline=False)
    py_ver=platform.python_version()
    embed.add_field(name=_("status.python", uid), value=py_ver, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def setlang(ctx, l="ja"):
    """言語設定"""
    uid=ctx.author.id
    if l in localize.AVAILABLE:
        localize.setlocale(uid, l)
        localize.update()
        localize.getlocale(0)
        await ctx.send(_("bot.languageChanged", uid))
    else:
        await ctx.send(_("bot.badLanguage", uid))

@bot.command()
@c.is_owner()
async def exit(ctx):
    """Owner only; exit command."""
    sys.exit()

@bot.command()
@c.is_owner()
async def clear_cache(ctx):
    """Owner only; cache clear command."""
    clear_synth()

@bot.command()
@c.is_owner()
async def reload(ctx):
    """Reload the translations."""
    localize.update()
    localize.getlocale(0)

@bot.command()
@c.is_owner()
async def demojy(ctx, emj):
    """テスト用: Demojy"""
    await ctx.send(f"`{emojy.demojize(emj)}`")

@bot.command()
async def hello(ctx):
    """ こんにちわんこ。 """
    await ctx.send(_("bot.hello", ctx.author.id))

# From kenny2automate
@bot.command()
@c.is_owner()
@c.has_permissions(manage_messages=True, read_message_history=True)
@c.bot_has_permissions(manage_messages=True, read_message_history=True)
async def purge(ctx, limit: int = 100, user: d.Member = None, *, matches: str = None):
	"""Purge all messages, optionally from ``user``
	or contains ``matches``."""
	def check_msg(msg):
		if msg.id == ctx.message.id:
			return True
		if user is not None:
			if msg.author.id != user.id:
				return False
		if matches is not None:
			if matches not in msg.content:
				return False
		return True
	deleted = await ctx.channel.purge(limit=limit, check=check_msg)

@c.guild_only()
@bot.command()
async def here(ctx):
    """@here"""
    GUILDID = 497978199087775754
    ROLEID = 499905665637023786
    uid=ctx.author.id
    guild=ctx.guild
    if guild.id != GUILDID:
        await ctx.send(_("here.noGuild", uid))
        return
    role = guild.get_role(ROLEID)
    if not role:
        await ctx.send(_("here.noRole", uid))
        return
    mntn = _("here.mention", uid)
    for member in role.members:
        if member.status in (d.Status.online, d.Status.idle):
            mntn += '{0}\n'.format(member.mention)
    await ctx.send(mntn)

@bot.command()
async def ping(ctx):
    """Ping!"""
    now_dt=datetime.utcnow()
    now=now_dt.timestamp()
    uid=ctx.author.id
    rt=ctx.message.created_at.timestamp()
    now2_dt=datetime.utcnow()
    now2=now2_dt.timestamp()
    msg = await ctx.send(_("ping.receive", uid, int(abs(now-rt)*1000)/1000))
    st=msg.created_at.timestamp()
    await msg.edit(content=msg.content+'\n'+_("ping.sent", uid, int(abs(now2-st)*1000)/1000))

@c.guild_only()
@bot.command()
async def invite(ctx, mention):
    """Get invite url of a bot"""
    mntn=m2m(mention, ctx)
    uid=ctx.author.id
    if not (mntn and mntn.bot):
        await ctx.send(_("invite.notBot", uid))
        return
    perms=mntn.guild_permissions
    url=d.utils.oauth_url(mntn.id, perms)
    await ctx.author.create_dm()
    dm=ctx.author.dm_channel
    warn_text=""
    if perms.administrator:
        warn_text=emojy.emojize(_("invite.admin", uid, ":warning:"))
    else:
        if (perms.ban_members or perms.kick_members):
            warn_text+=emojy.emojize(_("invite.kicking", uid, ":warning:"))+"\n"
        if (perms.manage_channels or perms.manage_messages):
            warn_text+=emojy.emojize(_("invite.deleteable", uid, ":warning:"))+"\n"
        if perms.create_instant_invite:
            warn_text+=emojy.emojize(_("invite.invitation", uid, ":warning:"))+"\n"
        if (perms.manage_nicknames or perms.mention_everyone):
            warn_text+=emojy.emojize(_("invite.confusing", uid, ":thinking_face:"))+"\n"
        if (perms.view_audit_log or perms.read_message_history):
            warn_text+=emojy.emojize(_("invite.secret", uid, ":Japanese_secret_button:"))+"\n"
    if warn_text:
        await dm.send(warn_text)
    perm_names=_("bot.sep", uid).join(map(lambda val:val[0], filter(lambda val:val[1],sorted(perms, key=lambda val:val[0]))))
    if perm_names:
        await dm.send(_("invite.permissions", uid, perm_names))
    else:
        await dm.send(_("invite.strangely", uid))
    await dm.send(embed=d.Embed(description='[{1}]({0})'.format(url, _("invite.click", uid))))

def _req2(url):
    CHROME="Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    resp=requests.get(url, headers={
        'Cache-Control': 'max-age=0',
        'User-Agent':CHROME,
        'Accept-Language':'ja, en;q=0.9, zh;q=0.8, *;q=0.5'
    })
    if resp.status_code >= 400:
        return None
    else:
        return resp.text

def itime():
    return int(time.time())

async def translater(ctx,lang="ja",txt=None):
    uid=ctx.author.id
    if True:
        global TRANSLATELIMIT
        if time.time() < TRANSLATELIMIT + 5:
            await ctx.send(_("translate.rateLimit", uid))
            return
        if txt == None:
            return
        resp=_req2("https://translate-service.scratch.mit.edu/supported")
        if resp == None:
            return
        respjson=json.loads(resp)
        supported=map(lambda x:x["code"],respjson["result"])
        if lang not in supported:
            lang="ja"
        addr="https://translate-service.scratch.mit.edu/translate?language={0}&text={1}".format(lang,txt)
        resp=_req2(addr)
        if resp == None:
            return
        await ctx.send(json.loads(resp)["result"])
        TRANSLATELIMIT = time.time()
        return

@bot.command()
async def translate(ctx,lang="ja",*,txt=None):
    """ 翻訳機能 """
    if lang in ('p','pinyin', 'pyn', '拼'):
        pinyins=list(map(lambda pron: pron.capitalize(), pypinyin.lazy_pinyin(txt)))
        await ctx.send(' '.join(pinyins))
    elif lang in ('b','bopo', 'bopomofo', '注'):
        bopomofos=list(map(lambda pron: pron[0], pypinyin.pinyin(txt, style=pypinyin.Style.BOPOMOFO)))
        await ctx.send(' '.join(bopomofos))
    else:
        await translater(ctx,lang,txt)

SYNTH_LIMIT=0

@bot.command()
async def tts(ctx, text, gender='male', locale='ja-JP'):
    """音声合成です"""
    global SYNTH_LIMIT
    uid=ctx.author.id
    if SYNTH_LIMIT+20 > itime():
        await ctx.send(_("tts.rateLimit", uid))
        return
    async with ctx.typing():
        text=quote(text)
        url=f"https://synthesis-service.scratch.mit.edu/synth?locale={locale}&gender={gender}&text={text}"
        filename=f"./synth/{itime()}.mp3"
        with open(filename, 'wb') as f:
            stream(f, url)
        with open(filename, 'rb') as f2:
            dfile=d.File(f2, 'text2speech.mp3')
            await ctx.send(file=dfile)
    SYNTH_LIMIT=itime()

@bot.command()
async def scratchnews(ctx):
    """ Scratch News! """
    global SCRATCHLIMIT
    uid=ctx.author.id
    if time.time() < SCRATCHLIMIT + 10:
        await ctx.send(_("news.rateLimit", uid))
        return
    SCRATCHLIMIT=time.time()
    news=scratchapi2.FrontPage().news()
    embed = d.Embed(
        title=_("news.title", uid),
        description=_("news.description", uid),
        color=0xffab1a
    )
    for content in news:
        embed.add_field(
            name=_("news.newstitle", uid),
            value=content.title
        )
        embed.add_field(
            name=_("news.content", uid),
            value=content.description
        )
        embed.add_field(
            name=_("news.date", uid),
            value=content.timestamp
        )
        if content.url:
            embed.add_field(
                name=_("news.url", uid),
                value=content.url
            )
    await ctx.send(embed=embed)

class GenericData(object):
    """Base class for other data objects created on the fly."""

    _repr_str = None

    def __init__(self, **kwargs):
        """Initialize object by updating __dict__ with kwargs."""
        self.__dict__.update(kwargs)

    def __repr__(self):
        if self._repr_str:
            return self._repr_str.format(**self.__dict__)
        return '<GenericData>'

    __str__ = __repr__

def _parsefeed(feed):
    soup = bs4.BeautifulSoup(feed, "lxml-xml")
    entries = soup.find_all("entry")
    arr = []
    for entry in entries:
        summary=bs4.BeautifulSoup(unescape(entry.summary.string), "html.parser").get_text().strip()
        if len(summary)>97:
            summary=summary[0:97]+"..."
        arr.append(GenericData(
            title=entry.title.string,
            user=entry.author.find("name").string,
            url=entry.link['href'],
            time=entry.published.string,
            summary=summary
        ))
    return arr

@bot.command()
async def newpost(ctx, forumid="18"):
    """ フォーラムの最新投稿 """
    global FORUMLIMIT
    uid=ctx.author.id
    if time.time() < FORUMLIMIT + 10:
        await ctx.send(_("forum.rateLimit",uid))
        return
    FORUMLIMIT=time.time()
    try:
        _int_id=int(forumid)
    except:
        await ctx.send(_("forum.forumIdError",uid))
        return
    source="https://scratch.mit.edu/discuss/feeds/forum/"+forumid
    feedfile=_req2(source)
    if feedfile is None:
        await ctx.send(_("forum.error",uid))
        return
    feeds=_parsefeed(feedfile)
    embed = d.Embed(title=_("forum.forumTitle",uid), description=_("forum.description",uid), color=randint(0,0xFFFFFF))
    for feed in feeds:
        embed.add_field(
            name=_("forum.topic",uid),
            value=feed.title,
            inline=True
        )
        embed.add_field(
            name=_("forum.author",uid),
            value=feed.user,
            inline=True
        )
        embed.add_field(
            name=_("forum.date",uid),
            value=feed.time,
            inline=True
        )
        embed.add_field(
            name=_("forum.content",uid),
            value=feed.summary,
            inline=True
        )
        embed.add_field(
            name=_("forum.url",uid),
            value=feed.url,
            inline=True
        )
    await ctx.send(embed=embed)

@bot.command()
async def newposttopic(ctx, topicid="312512"):
    """ トピックの最新投稿 """
    global FORUMLIMIT
    uid=ctx.author.id
    if time.time() < FORUMLIMIT + 10:
        await ctx.send(_("forum.rateLimit",uid))
        return
    FORUMLIMIT=time.time()
    try:
        _int_id=int(topicid)
    except:
        await ctx.send(_("forum.topicIdError",uid))
        return
    source="https://scratch.mit.edu/discuss/feeds/topic/"+topicid
    feedfile=_req2(source)
    if feedfile is None:
        await ctx.send(_("forum.error",uid))
        return
    feeds=_parsefeed(feedfile)
    embed = d.Embed(title=_("forum.topicTitle",uid), description=_("forum.description",uid), color=randint(0,0xFFFFFF))
    for feed in feeds:
        embed.add_field(
            name=_("forum.author",uid),
            value=feed.user,
            inline=True
        )
        embed.add_field(
            name=_("forum.date",uid),
            value=feed.time,
            inline=True
        )
        embed.add_field(
            name=_("forum.content",uid),
            value=feed.summary,
            inline=True
        )
        embed.add_field(
            name=_("forum.url",uid),
            value=feed.url,
            inline=True
        )
    await ctx.send(embed=embed)

@bot.command()
async def eqinfo(ctx):
    """ 地震情報 """
    global P2PLIMIT
    uid=ctx.author.id
    if time.time() < P2PLIMIT + 20:
        await ctx.send(_("eq.rateLimit", uid))
        return
    P2PLIMIT=time.time()
    parsedeq=eqapi.parseapi(eqapi.geteqapi())
    if parsedeq is None:
        await ctx.send(_("eq.errorExpected", uid))
    elif type(parsedeq) == eqapi.EqData:
        embed = d.Embed(title=eqapi.infos[parsedeq.infotype],
                        description="by p2pquake API",
                        color=0xFF0000
                        )
        embed.add_field(name=_("eq.time", uid),value=parsedeq.time,inline=True)
        embed.add_field(name=_("eq.hypoName", uid),value=parsedeq.hyponame,inline=True)
        embed.add_field(name=_("eq.lat", uid),value=parsedeq.lat,inline=True)
        embed.add_field(name=_("eq.long", uid),value=parsedeq.long,inline=True)
        embed.add_field(name=_("eq.depth", uid),value=parsedeq.depth,inline=True)
        embed.add_field(name=_("eq.mag", uid),value=parsedeq.mag,inline=True)
        embed.add_field(name=_("eq.tsunami", uid),value=eqapi.tsunamidic[parsedeq.tsunami],inline=True)
        embed.add_field(name=_("eq.maxScale", uid),value=eqapi.eq2level[parsedeq.maxScale],inline=True)
        await ctx.send(embed=embed)
        for point in parsedeq.points:
            pem = d.Embed(title=_("eq.scaleDetail", uid),description=_("eq.scaleDetailDesc", uid),color=eqapi.getcolor(point["scale"]))
            pem.add_field(name=_("eq.scaleAddress", uid),value=point["addr"])
            pem.add_field(name=_("eq.scale", uid),value=eqapi.eq2level[point["scale"]])
            await ctx.send(embed=pem)
    elif type(parsedeq) == eqapi.Tsunami:
        embed = d.Embed(title=_("eq.tsunamiInfo", uid),
                        description="by p2pquake API",
                        color=0xFF0000
                        )
        if not parsedeq.cancel:
            for point in parsedeq.areas:
                pem = d.Embed(title=_("eq.tsunamiDetail", uid),description=_("eq.tsunamiDetailDesc", uid),color=0xFF0000)
                pem.add_field(name=_("eq.tsunamiAddress", uid),value=point["name"])
                pem.add_field(name=_("eq.tsunamiLevel", uid),value=eqapi.tinfos[point["grade"]])
                await ctx.send(embed=pem)

def clampstr(s,l):
    s=s.replace("\n","").replace("\r","")
    if len(s)>l:
        return s[:l]+"..."
    else:
        return s

@bot.command()
async def ghissue(ctx, un="llk", repo="scratch-gui"):
    """ GitHubのIssueを取得 初期値:llk/scratch-gui """
    global GHLIMIT
    uid=ctx.author.id
    if time.time() < GHLIMIT + 20:
        await ctx.send(_("github.rateLimit", uid))
        return
    GHLIMIT=time.time()
    g=github3.GitHub()
    issues = list(g.issues_on(un, repo, state="open", number=2))
    for issue in issues:
        embed = d.Embed(title=_("github.title", uid, un, repo),
                        description=_("github.description", uid),
                        color=randint(0,0xFFFFFF))
        embed.add_field(name=_("github.issueTitle", uid), value=clampstr(issue.title,97) or "Error", inline=True)
        embed.add_field(name=_("github.issueContent", uid), value=clampstr(bs4.BeautifulSoup(issue.body,"html.parser").get_text(),97) or _("github.error", uid), inline=True)
        embed.add_field(name=_("github.issueAuthor", uid), value=issue.user or _("github.error", uid), inline=True)
        embed.add_field(name=_("github.issueDate", uid), value=issue.created_at or _("github.error", uid), inline=True)
        embed.add_field(name=_("github.issueLabel", uid), value=",".join(list(map(str, list(issue.labels())))) or _("github.none", uid), inline=True)
        embed.add_field(name=_("github.url", uid), value=issue.html_url or _("github.error", uid), inline=True)
        await ctx.send(embed=embed)

@bot.command()
@c.cooldown(1, 60)
async def wiki(ctx, page, wikicode='ja'):
    """Japanese Scratch-Wikiのページを取得します。"""
    uid=ctx.author.id
    wikidic={
        "ja": "https://ja.scratch-wiki.info/w/api.php",
        "en": "https://en.scratch-wiki.info/w/api.php",
        "enwp": "https://en.wikipedia.org/w/api.php",
        "ep": "https://enpedia.rxy.jp/w/api.php"
    }
    async with ctx.channel.typing():
        try:
            jaw=mwc.Wiki(wikidic.get(wikicode, wikidic["ja"]), "GigaAppleBot (only read)")
            await ctx.trigger_typing()
            try:
                with open("./settings/wiki_login.txt", "r", encoding="utf-8") as pwd:
                    user=pwd.readline()
                    passwd=pwd.readline()
                    jaw.login(user, passwd)
            except:
                pass # This is not required
            pg=jaw.page(page)
            await ctx.trigger_typing()
            first=list(pg.revisions(limit=1, rvdir="newer"))[0]
            await ctx.trigger_typing()
            try:
                await ctx.trigger_typing()
                scratch_user=scratchapi2.User(first.user)
                icon_url=scratch_user.images["60x60"]
            except:
                #Bots
                icon_url="https://cdn2.scratch.mit.edu/get_image/user/default_60x60.png"
            page_url="https://ja.scratch-wiki.info/wiki/{0}".format(quote(page))
            userpage_url="https://ja.scratch-wiki.info/w/index.php?title={0}&action=history".format(quote(page))
            await ctx.trigger_typing()
            page_parsed=jaw.request(
                action="parse",
                page=page,
                prop="images|parsetree"
            )["parse"]
            try:
                img=page_parsed["images"][0]
                await ctx.trigger_typing()
                img_url=list(jaw.request(
                    action="query",
                    prop="imageinfo",
                    titles="File:{0}".format(img),
                    iiprop="url"
                )["query"]["pages"].values())[0]["imageinfo"][0]["url"]
            except IndexError:
                img_url=None
            await ctx.trigger_typing()
            page_content_xmled=bs4.BeautifulSoup(page_parsed["parsetree"]["*"],"xml")
            page_content_str=""
            for maybe_tag in page_content_xmled.find("root").contents:
                if type(maybe_tag) is bs4.element.NavigableString:
                    page_content_str+=str(maybe_tag)
            page_content_str=re.sub("\n+", "\n", page_content_str)
            page_content_str=re.sub("''(?P<italic>[^']+)'","*\g<italic>*",page_content_str)
            page_content_str=re.sub("'''(?P<bold>[^']+)'''","**\g<bold>**",page_content_str)
            page_content_str=re.sub("\[\[(File|ファイル|file)[^]]+\]\]","",page_content_str)
            page_content_embed=clampstr(page_content_str,500)
            await ctx.trigger_typing()
            embed=d.Embed(
                title=page,
                description=_("jawiki.desc", uid),
                url=page_url,
                color=randint(0,0xFFFFFF)
            )
            if img_url:
                embed.set_thumbnail(url=img_url)
            embed.set_author(name=_("jawiki.author",uid,first.user), url=userpage_url, icon_url=icon_url)
            embed.set_footer(text="Content is under CC BY-SA 4.0", icon_url="http://u.cubeupload.com/apple502j/sqhJHk.png")
            embed.add_field(name=_("jawiki.content",uid), value=page_content_embed, inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            try:
                traceback.print_exc()
                err_d=e.__class__().__repr__().replace("()","")
                await ctx.send(_("jawiki.error", uid, err_d))
                return
            except:
                raise e

@bot.command()
async def birthday(ctx, *, person="Abe Shinzo"):
    """ 誕生日 """
    uid=ctx.author.id
    RQHEAD={"User-Agent":"GigaAppleBot via requests (apple502j)"}
    p=escape(person)
    try:
        rsp1=requests.get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search={p}&language=en&type=item&limit=1", params=RQHEAD).json()
    except:
        await ctx.send(_("birthday.notFound", uid))
        return
    try:
        iid=rsp1["search"][0]["id"]
        rsp2=requests.get(f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={iid}&sites=jawiki&props=info%7Clabels%7Cdescriptions%7Cclaims%7Cdatatype&languages=ja%7Cen", params=RQHEAD).json()
    except:
        await ctx.send(_("birthday.notFound", uid))
        return
    try:
        birth=rsp2["entities"][iid]["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
        bd=datetime.strptime(birth, "+%Y-%m-%dT00:00:00Z")
        bdstr=bd.strftime("%Y/%m/%d")
        await ctx.send(bdstr)
        return
    except:
        await ctx.send(_("birthday.notRegistered", uid))
        return

MEMORIZING=False

@bot.command()
async def morize(ctx):
    """ 暗記ゲーム """
    global MEMORIZING
    uid=ctx.author.id
    if MEMORIZING:
        await ctx.send(_("game.otherGame", uid))
        return
    MEMORIZING=True
    LC=[":dollar_banknote:",":yen_banknote:",":euro_banknote:",":pound_banknote:"]
    LS=[":globe_showing_Americas:",":globe_showing_Europe-Africa:",":globe_showing_Asia-Australia:",":map_of_Japan:"]
    LO=[":money_mouth:",":musical_keyboard:",":ramen:",":baggage_claim:",":mouse:",
        ":statue_of_liberty:",":ocean:",":tokyo_tower:", ":battery:", ":full_moon:"]
    randy=[]
    for i in range(randint(1,4)):
        randy.append(LC[randint(0,3)])
    for i in range(randint(1,4)):
        randy.append(LS[randint(0,3)])
    shuffle(randy)
    def getemoji(c):
        if len(c)==2:
            return ec(c)
        return emojy.emojize(c)
    ankey=''.join(list(map(getemoji, randy)))
    for i in range(randint(1,10)):
        randy.insert(randint(0, len(randy)-1), LO[randint(0, 9)])
    ankey2=''.join(list(map(getemoji, randy)))
    await ctx.send(_("memorize.description", uid))

    msg=await ctx.send(_("memorize.memorize", uid, ankey2))
    time.sleep(3)
    await msg.delete()
    def chk(ms):
        return (
            ms.channel==ctx.channel and
            ms.content.replace(" ","")==ankey
            )
    await ctx.send(_("memorize.send", uid))
    try:
        mee=await bot.wait_for('message', check=chk, timeout=30)
        await ctx.send(_("game.good", uid, mee.author.mention))
        mo=Money(bot, MONEY_TRANSFER_INFO).getum(mee.author.id)
        mo+=20
        Money(bot, MONEY_TRANSFER_INFO).setum(mee.author.id, mo)
        MEMORIZING=False
        return
    except asyncio.TimeoutError:
        await ctx.send(_("game.answer", uid, ankey))
        MEMORIZING=False
        return

LONGWORDING = False
@bot.command()
async def longandright(ctx, level):
    """長い単語を正しくつづろう"""
    global LONGWORDING
    uid=ctx.author.id
    try:
        level=int(level)
        assert level in (1,2,3)
    except:
        await ctx.send(_("longandright.invalidLv", uid))
        return
    if LONGWORDING:
        await ctx.send(_("game.otherGame", uid))
        return
    else:
        LONGWORDING=True
    lvwords=LONG_WORDS["words"][level-1]
    word=randchoice(lvwords)
    sorted_word=sortstr(word)
    await ctx.send(_("longandright.word", uid, sorted_word))
    def chk(ms):
        return (
            ms.channel==ctx.channel and
            ms.content==word
            )
    try:
        mee=await bot.wait_for('message', check=chk, timeout=30)
        await ctx.send(_("game.good", uid, mee.author.mention))
        mo=Money(bot, MONEY_TRANSFER_INFO).getum(mee.author.id)
        mo+=(level * 20)
        Money(bot, MONEY_TRANSFER_INFO).setum(mee.author.id, mo)
        LONGWORDING=False
        return
    except asyncio.TimeoutError:
        await ctx.send(_("game.answer", uid, word))
        LONGWORDING=False
        return

@bot.command(name='penalty')
@c.cooldown(1, 120, type=c.BucketType.user)
@c.bot_has_permissions(read_message_history=True, add_reactions=True, manage_messages=True)
async def pk(ctx):
    uid=ctx.author.id
    win=False
    emojis=[emojy.emojize(e) for e in (':up-left_arrow:', ':fast_up_button:', ':upwards_button:', ':up_arrow:', ':up-right_arrow:')]
    msg = await ctx.send(_("pk.wait", uid))
    pk=randint(0, 4)
    print(f"cheat: {pk}")
    pk_emoji=""
    for i in range(5):
        if i == pk:
            pk_emoji += emojy.emojize(":heavy_large_circle:")
        else:
            pk_emoji += emojy.emojize(":cross_mark:")
    def chk(r):
        return str(r.emoji) in emojis and r.message_id == msg.id and r.user_id == uid
    async with ctx.typing():
        for emoji in emojis:
            await msg.add_reaction(emoji)
        embed=d.Embed(title=_("pk.title", uid), description=_("pk.situation", uid), color=randint(0, 0xffffff))
        embed.set_image(url="http://u.cubeupload.com/apple502j/ljPH7f.png")
        await msg.edit(embed=embed)
    try:
        r = await bot.wait_for("raw_reaction_add", check=chk, timeout=60)
        await msg.remove_reaction(str(r.emoji), ctx.author)
        chosen = emojis.index(str(r.emoji))
        pk_emoji = ""
        for i in range(5):
            if i == pk:
                pk_emoji += emojy.emojize(":heavy_large_circle:")
            elif i == chosen:
                pk_emoji += emojy.emojize(":soccer_ball:")
            else:
                pk_emoji += emojy.emojize(":cross_mark:")
        embed.add_field(name=_("pk.shoot", uid), value=pk_emoji)
        await msg.edit(embed=embed)
        if pk == chosen:
            win=True
            mo=Money(bot, MONEY_TRANSFER_INFO).getum(ctx.author.id)
            mo+=10
            Money(bot, MONEY_TRANSFER_INFO).setum(ctx.author.id, mo)
    except a.TimeoutError:
        await ctx.send(_("pk.timeout",uid))
        embed.add_field(name=_("pk.shoot", uid), value=pk_emoji)
        await msg.edit(embed=embed)
    await ctx.send(_("pk.gameEnded", uid))
    if win:
        await ctx.send(_("pk.win", uid))

print("Do")
bot.run(TOKEN)
