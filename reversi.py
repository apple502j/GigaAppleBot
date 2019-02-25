from enum import IntEnum
import asyncio as a
import re
import random
import discord as d
from discord.ext import commands as c
from emoji import emojize
from localize import _
from util import Range, CogHelper
from money import Money

DOING = []

class CannotPut(Exception):
    pass

class Stone(IntEnum):
    CPU = 1
    PLAYER = 2
    EMPTY_SPACE = 0

class Turn(IntEnum):
    PLAYER = 1
    CPU = 0

class Reversi(CogHelper):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def is_range(x, y):
        return x in Range(0, 7) and y in Range(0, 7)

    def valid(self, board, tile, xstart, ystart):
        # From flippy
        # Returns False if the player's move is invalid. If it is a valid
        # move, returns a list of spaces of the captured pieces.
        if not self.is_range(xstart, ystart) or board[xstart][ystart] != Stone.EMPTY_SPACE:
            print(f"it is {board[xstart][ystart]}")
            raise CannotPut

        board[xstart][ystart] = tile # temporarily set the tile on the board.

        if tile == Stone.CPU:
            otherTile = Stone.PLAYER
        else:
            otherTile = Stone.CPU

        tilesToFlip = []
        # check each of the eight directions:
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            if self.is_range(x, y) and board[x][y] == otherTile:
                # The piece belongs to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not self.is_range(x, y):
                    continue
                while board[x][y] == otherTile:
                    x += xdirection
                    y += ydirection
                    if not self.is_range(x, y):
                        break # break out of while loop, continue in for loop
                if not self.is_range(x, y):
                    continue
                if board[x][y] == tile:
                    # There are pieces to flip over. Go in the reverse
                    # direction until we reach the original space, noting all
                    # the tiles along the way.
                    while True:
                        x -= xdirection
                        y -= ydirection
                        if x == xstart and y == ystart:
                            break
                        tilesToFlip.append([x, y])

        board[xstart][ystart] = Stone.EMPTY_SPACE # make space empty
        if len(tilesToFlip) == 0: # If no tiles flipped, this move is invalid
            raise CannotPut
        return tilesToFlip

    def move(self, board, tile, x, y):
        tiles = self.valid(board, tile, x, y)
        if not tiles:
            raise CannotPut
        for ox, oy in tiles:
            board[ox][oy] = tile
        board[x][y] = tile

    def all_valid(self, board, turn):
        returns=[]
        for x in range(0, 7):
            for y in range(0, 7):
                try:
                    if self.valid(board, turn, x, y):
                        returns.append((x, y))
                        print(f"can put: {x}{y}")
                except CannotPut:
                    print(f"Cannot put: {x}{y}")
                    continue
        return returns

    async def draw_board(self, user, msg, board, turn, status):
        emoji = (
            emojize(":black_large_square:"),
            emojize(":white_circle:"),
            emojize(":red_circle:")
        )
        uid=user.id
        numemoji=("1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣","8⃣")
        boardstr=emojize(":black_large_square:"+''.join(numemoji))+"\n"
        for bx in range(8):
            boardstr+=emojize(numemoji[bx])
            for by in range(8):
                boardstr+=emoji[board[bx][by]]
            boardstr+="\n"
        turn_msg=_("reversi.myTurn", uid) if turn==Turn.CPU else _("reversi.yourTurn", uid)
        turn_color=0xFF0000 if turn==Turn.PLAYER else 0xFFFFFF
        embed=d.Embed(title=_("reversi.title", uid, user.name, _("reversi.cpu", uid)), description=turn_msg, color=turn_color)
        embed.add_field(name=_("reversi.status", uid), value=status, inline=True)
        embed.add_field(name=_("reversi.board", uid), value=boardstr, inline=False)
        await msg.edit(embed=embed)
        print("Drawn!")

    @staticmethod
    def get_stone(turn):
        return Stone.CPU if turn==Turn.CPU else Stone.PLAYER

    @c.command()
    @c.is_owner()
    async def force(self, ctx):
        global DOING
        DOING=False

    @c.command()
    @c.bot_has_permissions(manage_messages=True)
    async def reversi(self, ctx):
        """Reversi!"""
        global DOING
        giveup=False
        uid=ctx.author.id
        if ctx.channel.id in DOING:
            await ctx.send(_("game.otherGame", uid))
            return
        await ctx.trigger_typing()
        msg = await ctx.send(_("game.wait", uid))

        DOING.append(ctx.channel.id)
        board=[[Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.CPU, Stone.PLAYER, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.PLAYER, Stone.CPU, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE],
               [Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE, Stone.EMPTY_SPACE]
              ]

        print("Just before while")
        while_looper=0
        status_text=_("reversi.justBegan", uid)
        while True:
            while_looper+=1
            turn = Turn.PLAYER
            print(f"{while_looper}th {turn}")
            await self.draw_board(ctx.author, msg, board, turn, status_text)
            if not self.all_valid(board, self.get_stone(Turn.PLAYER)):
                break
            def check_msg(msg2):
                return msg2.author == ctx.author and msg2.channel == ctx.channel and re.match("([1-8]){2}|EXIT", msg2.content)
            try:
                answer=await self.bot.wait_for("message", check=check_msg, timeout=60)
                if answer.content == "EXIT":
                    giveup=True
                    break
            except a.TimeoutError:
                await ctx.send(_("reversi.timeout", uid))
                DOING=False
                return
            playery=int(answer.content[0])-1
            playerx=int(answer.content[1])-1
            await answer.delete()
            try:
                self.move(board, Stone.PLAYER, playerx, playery)
                status_text=_("reversi.youPut", uid, playerx+1, playery+1)
            except CannotPut:
                await ctx.send(_("reversi.cantPut", uid), delete_after=3)
                continue

            turn=Turn.CPU
            await self.draw_board(ctx.author, msg, board, turn, status_text)
            async with ctx.typing():
                await a.sleep(1)

                valid_steps=self.all_valid(board, self.get_stone(Turn.CPU))
                print(valid_steps)
                random.shuffle(valid_steps)
                for cpux,cpuy in valid_steps:
                    try:
                        self.move(board, Stone.CPU, cpux, cpuy)
                        break
                    except CannotPut:
                        continue
            status_text=_("reversi.iPut", uid, cpux+1, cpuy+1)
        cpu_pt=0
        player_pt=0
        print(board)
        for a1 in board:
            for a2 in a1:
                if a2==Stone.CPU:
                    cpu_pt+=1
                elif a2==Stone.PLAYER and not giveup:
                    player_pt+=1
        await self.draw_board(ctx.author, msg, board, turn, _("reversi.ended", uid))
        await ctx.send(_("reversi.result", uid, cpu_pt, player_pt))
        if cpu_pt < player_pt:
            user_k=Money.getum(uid)
            user_k+=(player_pt-cpu_pt)
            Money.setum(uid, user_k)
        #self.bot.remove_listener(on_raw_reaction_add)
        DOING.remove(ctx.channel.id)
