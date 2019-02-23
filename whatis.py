"""A module that results detail of something."""
import json
import traceback
import datetime
from typing import Union, Optional
from emoji import emojize
import discord.ext.commands as c
import discord as d

from localize import _
import localize
from util import SafeList, RealMemberConverter

class WhatIs:
    def __init__(self, bot):
        self.bot=bot
        print("WhatIs Initialized")

    @c.group()
    async def detail(self, ctx):
        pass

    def to_member(self, user_class, requester):
        satisfiable=list(filter(lambda member: member.id == user_class.id and member.guild.get_member(requester.id) and member.guild.me, list(self.bot.get_all_members())))
        return SafeList(satisfiable).get(0, None)

    @detail.command()
    @c.is_owner()
    async def set(self, ctx, u:str, n:int, h:str):
        with open("./settings/user_badges.json", "r", encoding="utf-8") as badges:
            badge_json=json.load(badges)
        badge_json[u]={}
        badge_json[u]["nitro"]=bool(n) and n!="0"
        badge_json[u]["nitro_since"]=n
        badge_json[u]["hype"]=h
        with open("./settings/user_badges.json", "w", encoding="utf-8") as badges:
            json.dump(badge_json, badges)

    @detail.command()
    async def user(self, ctx, target: Optional[RealMemberConverter] = None):
        uid=ctx.author.id
        if not target:
            if hasattr(ctx, 'guild') and ctx.guild:
                target=ctx.author
            else:
                for guild in self.bot.guilds:
                    maybe_member=guild.get_member(uid)
                    if maybe_member:
                        print(f"Member on {maybe_member.guild}")
                        target=maybe_member
                        break

        if target is None:
            await ctx.send(_("whatis.notFound", uid, _("whatis.user", uid)))
            return

        if hasattr(ctx, 'guild') and target.guild == ctx.guild:
            enable_guild=True
        else:
            enable_guild=False
            await ctx.send(_("whatis.needGuild", uid))

        # target is confirmed to be member
        await ctx.author.create_dm()
        dm=ctx.author.dm_channel

        with open("./settings/user_badges.json", "r", encoding="utf-8") as badges:
            badge_json=json.load(badges)
        nitro=badge_json.get(str(target.id), {"nitro": False, "hype": None}).get("nitro", False)
        nitro_since=badge_json.get(str(target.id), {"nitro_since": 0, "hype": None}).get("nitro_since", 0)
        nitro_since=datetime.date.fromtimestamp(nitro_since)
        hype=badge_json.get(str(target.id), {"nitro": False, "hype": None}).get("hype", None)
        if hype=="b":
            hype="Brilliance"
        elif type=="bl":
            hype="Balance"
        elif type=="br":
            hype="Bravery"
        else:
            hype=_("whatis.none", uid)
        status_dict={
            d.Status.online: d.Colour.green(),
            d.Status.offline: d.Colour.darker_grey(),
            d.Status.idle: d.Colour.orange(),
            d.Status.dnd: d.Colour.red()
        }

        status_name={
            d.Status.online: _("whatis.online", uid, emojize(":white_heavy_check_mark:")),
            d.Status.offline: _("whatis.offline", uid, emojize(":sleeping_face:")),
            d.Status.idle: _("whatis.idle", uid, emojize(":zipper-mouth_face:")),
            d.Status.dnd: _("whatis.dnd", uid, emojize(":bell_with_slash:")),
        }

        bot_emoji = emojize(":robot_face:") if target.bot else ""
        mobile = emojize(":mobile_phone:") if target.is_on_mobile() else ""
        app = emojize(":desktop_computer:") if not mobile and target.desktop_status != d.Status.offline else ""
        web = emojize(":globe_with_meridians:") if not app and not bot_emoji and target.web_status != d.Status.offline else ""
        off = emojize(":cross_mark:") if not (bot_emoji or mobile or app or web) else ""

        owner_status=await self.bot.is_owner(target)

        playing_dict = {
            d.ActivityType.listening: _("whatis.listening", uid, emojize(":headphone:")),
            d.ActivityType.playing: _("whatis.playing", uid, emojize(":video_game:")),
            d.ActivityType.watching: _("whatis.watching", uid, emojize(":television:")),
            d.ActivityType.streaming: _("whatis.streaming", uid, emojize(":microphone:")),
            d.ActivityType.unknown: _("whatis.unknownPlaying", uid, emojize(":question_mark:")),
            'default': _("whatis.unknownPlaying", uid, emojize(":question_mark:")),
        }

        activity=SafeList(target.activities).get(0)

        if activity and hasattr(activity, 'start') and activity.start:
            starting=_("whatis.from",uid, activity.start.strftime("%Y/%m/%d %H:%M:%S"))
        else:
            starting=''
        if activity:
            playing=_("whatis.playingDetail", uid, activity.name, getattr(activity, "detail", _("whatis.unknownDetail", uid)), starting)
        else:
            playing=_("whatis.none", uid)

        muted_emoji=self.bot.get_emoji(547042470005964813)
        deafen_emoji=self.bot.get_emoji(547041667514105861)

        if target.voice:
            voice_status="{0}{1}".format(
            (muted_emoji if target.voice.mute or target.voice.self_mute else emojize(":microphone:")),
            (deafen_emoji if target.voice.deaf or target.voice.self_deaf else emojize(":headphone:")),
            )
        else:
            voice_status=emojize(":question_mark:")

        embed=d.Embed(title=target.name, description=_("whatis.infoOn", uid, "{0} {1}".format(target.name, emojize(":glowing_star:") if owner_status else "")), color=status_dict[target.status])
        embed.set_thumbnail(url=target.avatar_url_as(format="png", size=256))
        embed.add_field(name=_("whatis.username", uid), value=str(target), inline=True)
        embed.add_field(name=_("whatis.userid", uid), value=str(target.id), inline=True)
        embed.add_field(name=_("whatis.nowOn", uid, status_name[target.status]), value="{0}{1}{2}{3}{4}".format(bot_emoji, mobile, app, web, off), inline=True)
        embed.add_field(name=_("whatis.created", uid), value=target.created_at.strftime("%Y/%m/%d %H:%M:%S"), inline=True)
        embed.add_field(name=playing_dict[getattr(activity, 'type', 'default')], value=playing, inline=True)
        embed.add_field(name=_("whatis.voice", uid), value=voice_status, inline=True)
        embed.add_field(name=_("whatis.nitro", uid), value=_("whatis.nitroSince", uid, nitro_since.strftime("%Y/%m/%d")) if nitro else _("whatis.noNitro", uid))
        embed.add_field(name=_("whatis.hypesquad", uid), value=hype if hype else _("whatis.none", uid))

        await dm.send(embed=embed)
        if enable_guild:
            # Able to trust member is on ctx.guild
            if hasattr(target, 'nick') and target.nick:
                nick=target.nick
            else:
                nick=_("whatis.none", uid)

            color=target.color

            try:
                roles = _("bot.sep", uid).join([role.name for role in reversed(target.roles[1:])])
            except KeyError:
                roles = _("whatis.none", uid)

            try:
                perms = _("bot.sep", uid).join([i[0] for i in iter(target.guild_permissions) if i[1]])
            except KeyError:
                perms = _("whatis.none", uid)

            embed=d.Embed(title=target.name, description=_("whatis.onServer", uid, target.guild.name), color=color)
            embed.add_field(name=_("whatis.displayName", uid), value=str(target.display_name), inline=True)
            embed.add_field(name=_("whatis.nickName", uid), value=nick, inline=True)
            embed.add_field(name=_("whatis.color", uid), value=str(color.to_rgb()), inline=True)
            embed.add_field(name=_("whatis.topRole", uid), value=target.top_role, inline=True)
            embed.add_field(name=_("whatis.roles", uid), value=roles, inline=True)
            embed.add_field(name=_("whatis.guildPermissions", uid), value=perms, inline=True)
            embed.add_field(name=_("whatis.joined", uid), value=target.joined_at.strftime("%Y/%m/%d %H:%M:%S"), inline=True)
            await dm.send(embed=embed)



    @user.error
    async def user_error(self, ctx, error):
        traceback.print_exc()
