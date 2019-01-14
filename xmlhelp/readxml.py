import re
from bs4 import BeautifulSoup
import discord as d

def read_xml(name):
    if re.match(r"[./\\]", name):
        raise ValueError
    with open(f"./xmlhelp/helps/{name}.xml", "r") as f:
        return f.read()

class HelpSection:
    def __init__(self, title, content):
        self.title=title
        self.content=content

class Help:
    def __init__(self, title, desc, url, thumb, sections):
        self.title=title
        self.desc=desc
        self.url=url
        self.thumb=thumb
        self.sections=sections

def parse(xml):
    soup=BeautifulSoup(xml, "xml")
    title=soup.find("title").get_text()
    desc=soup.find("desc").get_text()
    try:
        url=soup.find("url").get_text()
    except:
        url=None
    try:
        thumb=soup.find("thumb").get_text()
    except:
        thumb=None
    sections=list(filter(lambda a:not isinstance(a,str), soup.find("sections").children))
    sections=list(map(lambda b:HelpSection(b.attrs["title"], b.get_text()),sections))
    return Help(title, desc, url, thumb, sections)

def make_embed(help_obj):
    embed=d.Embed(title=help_obj.title, description=help_obj.desc,url=help_obj.url,color=0xff8000)
    embed.set_author(name="Apple502j's Bot", url="https://apple502j.github.io", icon_url="http://u.cubeupload.com/apple502j/JaeVGl.jpg")
    embed.set_footer(text="Help is under CC BY-SA 4.0", icon_url="http://u.cubeupload.com/apple502j/sqhJHk.png")
    if help_obj.thumb:
        embed.set_thumbnail(url=help_obj.thumb)
    for section in help_obj.sections:
        embed.add_field(name=section.title, value=section.content, inline=False)
    return embed

def all_in_one(name):
    return make_embed(parse(read_xml(name)))
