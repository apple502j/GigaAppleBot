import asyncio as a
from time import time
from urllib.parse import quote
from io import BytesIO
import discord as d
from discord.ext import commands as c
from util import CogHelper, stream, not_found, Range
from localize import _

class ScratchTTS(d.PCMVolumeTransformer):
    def __init__(self, source, *, volume=0.5):
        super().__init__(source, volume)

    @classmethod
    async def from_params(cls, text, *, gender='male', locale='ja-JP', loop=None, volume=0.5):
        url=f"https://synthesis-service.scratch.mit.edu/synth?locale={locale}&gender={gender}&text={quote(text)}"
        loop = loop or a.get_event_loop()
        timestamp=time()
        with open(f"./synth/{timestamp}.mp3", "wb") as file:
            data = await loop.run_in_executor(None, lambda: stream(file, url))
        with open(f"./synth/{timestamp}.mp3", "rb") as file:
            return cls(d.FFmpegPCMAudio(file, pipe=True), volume=volume)

class Voice(CogHelper):
    def __init__(self, bot):
        self.bot=bot
        self.volume=0.5

    @c.group()
    async def voice(self, ctx):
        if not ctx.invoked_subcommand:
            await not_found(ctx)

    @staticmethod
    def get_voice_ch(guild):
        vcs=guild.voice_channels
        for vc in vcs:
            print(f"Guild {guild} VC {vc}")
            perms=guild.me.permissions_in(vc)
            if not (perms.connect and perms.speak):
                print(f"No permission: {vc}")
                vcs.remove(vc)
                continue
            if vc.members and not (len(vc.members) == 1 and vc.members[0] == guild.me):
                print(f"Has member: {vc.members} so VC {vc}")
                return vc
        print(f"Default: {0}")
        return vcs[0]

    async def join(self, ctx):
        ch=self.get_voice_ch(ctx.guild)
        if ctx.voice_client:
            if ctx.voice_client.channel == ch:
                print(f"Use current ch, {ch}")
                return
            print(f"Moved to {ch}")
            return await ctx.voice_client.move_to(ch)
        print(f"Connected to {ch}")
        await ch.connect()

    @staticmethod
    def after_play(err):
        self.bot.using_synth_cache=False
        if err:
            print(f'Player error: {err}')

    @voice.command()
    @c.is_owner()
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @voice.command()
    async def volume(self, ctx, vol:int):
        uid=ctx.author.id
        if vol in Range(0, 100):
            self.volume=vol/100
            await ctx.send(_("voice.volumeSet", uid, vol))
        else:
            await ctx.send(_("voice.volumeRange", uid))

    @c.cooldown(1, 20)
    @voice.command()
    async def tts(self, ctx, text, gender='male', locale='ja-JP'):
        """音声合成です"""
        self.bot.using_synth_cache=True
        await self.join(ctx)
        async with ctx.typing():
            player = await ScratchTTS.from_params(text, gender=gender, locale=locale, loop=self.bot.loop, volume=self.volume)
            ctx.voice_client.play(player, after=self.after_play)
        await ctx.send(_("voice.tts", ctx.author.id, text))
