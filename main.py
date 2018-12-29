from datetime import datetime # logger time
import sys
from random import randint, shuffle # random color
from html import escape, unescape # parse html
import re
import time # system timestamp
import json # parse json value
import asyncio # await/async
import requests # internet requests
import github3 # GitHub
from bs4 import BeautifulSoup # parser
import scratchapi2 # scratch news
from discord.ext import commands as c # bot commands
import discord as d # discord main
import eqapi # earthquake
import emoji as emojy
from emojiflags import lookup as ec

with open("token.txt") as tkn:
    TOKEN=tkn.read().strip()
TRANSLATELIMIT = 0
SCRATCHLIMIT = 0
P2PLIMIT = 0
FORUMLIMIT = 0
GHLIMIT = 0
bot = c.Bot(command_prefix="me:", pm_help=True, activity=d.Activity(name="^help"))

def catnese(word):
    sp=re.findall("."*randint(2,4),word)
    for i in range(len(sp)):
        if randint(0,1):
            sp[i]="にゃー"
        else:
            sp[i]="にゃ"
    return ''.join(sp)

@bot.event
async def on_raw_reaction_add(ev):
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
        await channel.send(catnese(text))
        return


@bot.event
async def on_message(msg):
    """ 返事 """
    ctx = await bot.get_context(msg)
    if msg.author.bot == True:
        return
    if "<@"+str(bot.user.id)+">" in msg.content:
        reply = f'{msg.author.mention} 何でしょうか?'
        await ctx.send(reply)
    await bot.invoke(ctx)


@bot.command()
@c.is_owner()
async def exit(ctx):
    sys.exit()

@bot.command()
async def hello(ctx):
    """ こんにちわんこ。 """
    await ctx.send("こんにちわんこ!")

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

async def translater(ctx,lang="ja",txt=None):
    if True:
        global TRANSLATELIMIT
        if time.time() < TRANSLATELIMIT + 5:
            await ctx.send("You need to wait 5 seconds between translating commands!")
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
async def translate(ctx,lang="ja",txt=None):
    """ 翻訳機能 """
    await translater(ctx,lang,txt)

@bot.command()
async def scratchnews(ctx):
    """ Scratch News! """
    global SCRATCHLIMIT
    if time.time() < SCRATCHLIMIT + 10:
        await ctx.send("You need to wait 10 seconds between translating commands!")
        return
    SCRATCHLIMIT=time.time()
    news=scratchapi2.FrontPage().news()
    embed = d.Embed(
        title="Scratchニュース",
        description="Scratchの最新ニュースです。",
        color=0xffab1a
    )
    for content in news:
        embed.add_field(
            name="タイトル",
            value=content.title
        )
        embed.add_field(
            name="内容",
            value=content.description
        )
        embed.add_field(
            name="配信日時",
            value=content.timestamp
        )
        if content.url:
            embed.add_field(
                name="詳細URL",
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
    soup = BeautifulSoup(feed, "lxml-xml")
    entries = soup.find_all("entry")
    arr = []
    for entry in entries:
        summary=BeautifulSoup(unescape(entry.summary.string), "html.parser").get_text().strip()
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
    if time.time() < FORUMLIMIT + 10:
        await ctx.send("You need to wait 10 seconds between translating commands!")
        return
    FORUMLIMIT=time.time()
    try:
        _int_id=int(forumid)
    except:
        await ctx.send("フォーラムID、あってますか?")
        return
    source="https://scratch.mit.edu/discuss/feeds/forum/"+forumid
    feedfile=_req2(source)
    if feedfile is None:
        await ctx.send("エラー?")
        return
    feeds=_parsefeed(feedfile)
    embed = d.Embed(title="フォーラム", description="最新の投稿です", color=randint(0,0xFFFFFF))
    for feed in feeds:
        embed.add_field(
            name="トピック",
            value=feed.title,
            inline=True
        )
        embed.add_field(
            name="投稿者",
            value=feed.user,
            inline=True
        )
        embed.add_field(
            name="日時",
            value=feed.time,
            inline=True
        )
        embed.add_field(
            name="内容",
            value=feed.summary,
            inline=True
        )
        embed.add_field(
            name="URL",
            value=feed.url,
            inline=True
        )
    await ctx.send(embed=embed)

@bot.command()
async def newposttopic(ctx, topicid="312512"):
    """ トピックの最新投稿 """
    global FORUMLIMIT
    if time.time() < FORUMLIMIT + 10:
        await ctx.send("You need to wait 10 seconds between translating commands!")
        return
    FORUMLIMIT=time.time()
    try:
        _int_id=int(topicid)
    except:
        await ctx.send("トピックID、あってますか?")
        return
    source="https://scratch.mit.edu/discuss/feeds/topic/"+topicid
    feedfile=_req2(source)
    if feedfile is None:
        await ctx.send("エラー?")
        return
    feeds=_parsefeed(feedfile)
    embed = d.Embed(title="トピック", description="最新の投稿です", color=randint(0,0xFFFFFF))
    for feed in feeds:
        embed.add_field(
            name="投稿者",
            value=feed.user,
            inline=True
        )
        embed.add_field(
            name="日時",
            value=feed.time,
            inline=True
        )
        embed.add_field(
            name="内容",
            value=feed.summary,
            inline=True
        )
        embed.add_field(
            name="URL",
            value=feed.url,
            inline=True
        )
    await ctx.send(embed=embed)

@bot.command()
async def eqinfo(ctx):
    """ 地震情報 """
    global P2PLIMIT
    if time.time() < P2PLIMIT + 20:
        await ctx.send("You need to wait 20 seconds between translating commands!")
        return
    P2PLIMIT=time.time()
    parsedeq=eqapi.parseapi(eqapi.geteqapi())
    if parsedeq is None:
        await ctx.send("エラー発生。でも想定内。")
    elif type(parsedeq) == eqapi.EqData:
        embed = d.Embed(title=eqapi.infos[parsedeq.infotype],
                        description="by p2pquake API",
                        color=0xFF0000
                        )
        embed.add_field(name="発生時刻",value=parsedeq.time,inline=True)
        embed.add_field(name="震源",value=parsedeq.hyponame,inline=True)
        embed.add_field(name="震源緯度",value=parsedeq.lat,inline=True)
        embed.add_field(name="震源経度",value=parsedeq.long,inline=True)
        embed.add_field(name="深さ",value=parsedeq.depth,inline=True)
        embed.add_field(name="マグニチュード",value=parsedeq.mag,inline=True)
        embed.add_field(name="津波",value=eqapi.tsunamidic[parsedeq.tsunami],inline=True)
        embed.add_field(name="最大震度",value=eqapi.eq2level[parsedeq.maxScale],inline=True)
        await ctx.send(embed=embed)
        for point in parsedeq.points:
            pem = d.Embed(title="震度詳細",description="震度詳細情報",color=eqapi.getcolor(point["scale"]))
            pem.add_field(name="観測点",value=point["addr"])
            pem.add_field(name="震度",value=eqapi.eq2level[point["scale"]])
            await ctx.send(embed=pem)
            print("api posted 1")
    elif type(parsedeq) == eqapi.Tsunami:
        embed = d.Embed(title="津波",
                        description="by p2pquake API",
                        color=0xFF0000
                        )
        if not parsedeq.cancel:
            for point in parsedeq.areas:
                pem = d.Embed(title="津波詳細",description="津波",color=0xFF0000)
                pem.add_field(name="予報区",value=point["name"])
                pem.add_field(name="階級",value=eqapi.tinfos[point["grade"]])
                await ctx.send(embed=pem)
                print("api posted 1")

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
    if time.time() < GHLIMIT + 20:
        await ctx.send("You need to wait 20 seconds between translating commands!")
        return
    GHLIMIT=time.time()
    g=github3.GitHub()
    issues = list(g.issues_on(un, repo, state="open", number=2))
    for issue in issues:
        embed = d.Embed(title=f"{un}/{repo}のIssue",
                        description="最新のIssueです。",
                        color=randint(0,0xFFFFFF))
        embed.add_field(name="タイトル", value=clampstr(issue.title,97) or "Error", inline=True)
        embed.add_field(name="投稿", value=clampstr(BeautifulSoup(issue.body,"html.parser").get_text(),97) or "Error", inline=True)
        embed.add_field(name="投稿者", value=issue.user or "Error", inline=True)
        embed.add_field(name="作成日", value=issue.created_at or "Error", inline=True)
        embed.add_field(name="ラベル", value=",".join(list(map(str, list(issue.labels())))) or "None", inline=True)
        embed.add_field(name="URL", value=issue.html_url or "Error", inline=True)
        await ctx.send(embed=embed)
        
@bot.command()
async def birthday(ctx, person="Abe Shinzo"):
    """ 誕生日 """
    RQHEAD={"User-Agent":"GigaAppleBot via requests (apple502j)"}
    p=escape(person)
    try:
        rsp1=requests.get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search={p}&language=en&type=item&limit=1", params=RQHEAD).json()
    except:
        await ctx.send("人が見つかりません")
        return
    try:
        iid=rsp1["search"][0]["id"]
        rsp2=requests.get(f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={iid}&sites=jawiki&props=info%7Clabels%7Cdescriptions%7Cclaims%7Cdatatype&languages=ja%7Cen", params=RQHEAD).json()
    except:
        await ctx.send("人が見つかりません")
        return
    try:
        birth=rsp2["entities"][iid]["claims"]["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
        bd=datetime.strptime(birth, "+%Y-%m-%dT00:00:00Z")
        bdstr=bd.strftime("%Y/%m/%d")
        await ctx.send(bdstr)
        return
    except:
        await ctx.send("誕生日が未登録です")
        return

MEMORIZING=False

@bot.command()
async def morize(ctx):
    """ 暗記ゲーム """
    global MEMORIZING
    if MEMORIZING:
        await ctx.send("ほかのゲームがあります!")
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
    await ctx.send("暗記ゲーム!")
    
    msg=await ctx.send("紙幣と地図のみ暗記してね: {}".format(ankey2))
    time.sleep(3)
    await msg.delete()
    def chk(ms):
        #print(emojy.demojize(ms.content))
        #print(emojy.demojize(ankey))
        return (
            ms.channel==ctx.message.channel and
            ms.content.replace(" ","")==ankey
            )
    await ctx.send("同じ並びの絵文字があるメッセージを送信してね。時間制限は30秒だよ!")
    try:
        mee=await bot.wait_for('message', check=chk, timeout=30)
        await ctx.send(f"{mee.author.mention}、正解!")
        MEMORIZING=False
        return
    except asyncio.TimeoutError:
        await ctx.send(f"正解は {ankey} でした! さようなら!")
        MEMORIZING=False
        return

print("Do")
bot.run(TOKEN)
