import discord

from discord.ext import commands
from inspect import cleandoc

from utils.utils import check_arg


class General(commands.Cog):
    """
    General commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.systems = ("3ds", "wiiu", "vwii", "switch", "nx", "ns", "wii", "dsi")

    async def simple_embed(self, ctx, text, *, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = cleandoc(text)
        await ctx.send(embed=embed)

    @commands.command()
    async def guide(self, ctx, *guides) -> None:
        """Links to the recommended guides"""
        guides = {x.lower() for x in guides if x.lower() in self.systems}

        if not guides:
            await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in self.systems])}.")
            return

        embed = discord.Embed(title="Guide")
        for x in guides:
            if check_arg(x, '3ds'):
                embed.set_author(name="Nintendo Homebrew & Plailect")
                embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
                embed.url = "https://3ds.hacks.guide/"
                embed.description = "A complete guide to 3DS custom firmware, from stock to boot9strap"
                await ctx.send(embed=embed)
                continue
            if check_arg(x, ('wiiu',)):
                embed.set_author(name="Nintendo Homebrew")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://wiiu.hacks.guide/"
                embed.description = "A guide collaboration between Nintendo Homebrew’s Helpers and Staff, from stock to CBHC custom firmware"
                await ctx.send(embed=embed)
                continue
            if check_arg(x, ('vwii',)):
                embed.set_author(name="Nintendo Homebrew")
                embed.set_thumbnail(url="https://i.imgur.com/FclGzNz.png")
                embed.url = "https://wiiu.hacks.guide/#/vwii-modding"
                embed.description = "vWii modding guide"
                await ctx.send(embed=embed)
                continue
            if check_arg(x, ('switch', 'nx', 'ns')):
                embed.set_author(name="Nintendo Homebrew")
                embed.set_thumbnail(url="https://i.imgur.com/CVSu1zc.png")
                embed.url = "https://switchgui.de/switch-guide/"
                embed.description = "A guide collaboration between Nintendo Homebrew's Helpers and Staff, from stock to Atmosphere"
                await ctx.send(embed=embed)
                continue
            if check_arg(x, 'wii'):
                embed.set_author(name="RiiConnect24")
                embed.set_thumbnail(url="https://i.imgur.com/KI6IXmm.png")
                embed.url = "https://wii.guide/"
                embed.description = "The complete guide to modding your Nintendo Wii"
                await ctx.send(embed=embed)
                continue
            if check_arg(x, 'dsi'):
                embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking")
                embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
                embed.url = "https://dsi.cfw.guide/"
                embed.description = "The complete guide to modding your Nintendo DSi"
                await ctx.send(embed=embed)

    @commands.command()
    async def twlfix(self, ctx):
        """Information on how to fix a broken TWL Partition"""
        await self.simple_embed(ctx, """
                                Follow [TWLFix-CFW](https://github.com/MechanicalDragon0687/TWLFix-CFW/releases/).
                                These instructions require that you **perform a system update** after running the app.
                                """, title="Fix broken TWL")

    @commands.command()
    async def unlaunch(self, ctx):
        """Installing Unlaunch"""
        embed = discord.Embed(title="Installing Unlaunch")
        embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking")
        embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
        embed.url = "https://dsi.cfw.guide/installing-unlaunch.html"
        embed.description = "How to install Unlaunch on the DSi"
        await ctx.send(embed=embed)

    @commands.command(aliases=["sd-card-setup", "sdformat"])
    async def formatsd(self, ctx):
        """Formatting your SD card"""
        embed = discord.Embed(title="SD Card Setup")
        embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking")
        embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
        embed.url = "https://dsi.cfw.guide/sd-card-setup.html"
        embed.description = "How to properly format your SD card"
        await ctx.send(embed=embed)

    @commands.command(aliases=["nanddump", "nandbackup"])
    async def nand(self, ctx):
        """Links to the NAND dumping guide"""
        embed = discord.Embed(title="Dumping NAND")
        embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking")
        embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
        embed.url = "https://dsi.cfw.guide/dumping-nand.html"
        embed.description = "How to dump your DSi's NAND"
        await ctx.send(embed=embed)

    @commands.command()
    async def dump(self, ctx, arg=None):
        """How to dump games and data for CFW consoles"""
        systems = ("3ds", "dsi", "dsiware")

        if arg not in systems:
            await ctx.send(f"Please specify a console. Valid options are: {', '.join([x for x in systems])}.")
            return

        if check_arg(arg, '3ds'):
            embed = discord.Embed(title="GodMode9 Dump Guide")
            embed.set_author(name="Nintendo Homebrew & Plailect")
            embed.set_thumbnail(url="https://nintendohomebrew.com/assets/img/nhplai.png")
            embed.url = "https://3ds.hacks.guide/dumping-titles-and-game-cartridges.html"
            embed.description = "How to dump Cartridges and Files on a 3DS using GodMode9"
            await ctx.send(embed=embed)
        elif check_arg(arg, ('dsi',)):
            embed = discord.Embed(title="GodMode9i Dump Guide")
            embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking")
            embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
            embed.url = "https://dsi.cfw.guide/dumping-game-cards.html"
            embed.description = "How to dump cartridges on a Nintendo DSi using GodMode9i"
            await ctx.send(embed=embed)
        elif check_arg(arg, ('dsiware',)):
            embed = discord.Embed(title="DSiWare Backups")
            embed.set_author(name="emiyl & DS⁽ⁱ⁾ Mode Hacking")
            embed.set_thumbnail(url="https://i.imgur.com/OGelKVt.png")
            embed.url = "https://dsi.cfw.guide/dsiware-backups.html"
            embed.description = "How to dump DSiWare on a Nintendo DSi using GodMode9i"
            await ctx.send(embed=embed)

    @commands.group(aliases=["crowdin"], invoke_without_command=True, case_insensitive=True)
    async def translate(self, ctx):
        """Links to Crowdin projects"""
        await ctx.send_help(ctx.command)

    async def tlembed(self, ctx, title, extension):
        embed = discord.Embed(title=title + " Crowdin Project")
        embed.set_author(name="DS-Homebrew Wiki")
        embed.set_thumbnail(url="https://support.crowdin.com/assets/logos/crowdin-white-symbol.png")
        embed.description = "Help translate " + title + " on Crowdin."
        embed.url = "https://crowdin.com/project/" + extension
        await ctx.send(embed=embed)

    @translate.command(aliases=["twlmenu", "twl", "twilightmenu"])
    async def twilight(self, ctx):
        await self.tlembed(ctx, "TWiLight Menu++", "TwilightMenu")

    @translate.command(aliases=["nds-bootstrap", "bootstrap", "ndsbs", "bs"])
    async def ndsbootstrap(self, ctx):
        await self.tlembed(ctx, "nds-bootstrap", "nds-bootstrap")

    @translate.command(aliases=["skins", "ds-homebrew.com", "website"])
    async def wiki(self, ctx):
        await self.tlembed(ctx, "DS-Homebrew Wiki", "ds-homebrew-wiki")

    @translate.command(aliases=["dsicfwguide", "dsi.cfw.guide"])
    async def dsiguide(self, ctx):
        await self.tlembed(ctx, "DSi Guide", "dsi-guide")

    @commands.command()
    async def color(self, ctx, *, arg=""):
        """Shows conversions of a color from #RRGGBB, #RGB, RRR GGG BBB, and BGR15"""

        arg = arg.replace("0x", "").replace("#", "")

        if len(arg) == 6:  # #RRGGBB
            rgb = (int(arg[0:2], 16), int(arg[2:4], 16), int(arg[4:6], 16))
        elif len(arg) == 3:  # #RGB
            rgb = (int(arg[0], 16) * 0x11, int(arg[1], 16) * 0x11, int(arg[2], 16) * 0x11)
        elif len(arg.split()) == 3:  # RRR GGG BBB
            split = arg.split()
            rgb = (max(min(int(split[0]), 0xFF), 0), max(min(int(split[1]), 0xFF), 0), max(min(int(split[2]), 0xFF), 0))
        elif len(arg) == 4:  # BGR15
            bgr15 = int(arg, 16)
            rgb = (round((bgr15 & 0x1F) * 0xFF / 0x1F), round(((bgr15 >> 5) & 0x1F) * 0xFF / 0x1F), round(((bgr15 >> 10) & 0x1F) * 0xFF / 0x1F))
        else:
            await ctx.send_help(ctx.command)
            return

        embed = discord.Embed(title="Color conversions")
        embed.color = rgb[0] << 0x10 | rgb[1] << 0x8 | rgb[2]
        embed.add_field(name="Hex (HTML)", value=f"`#{rgb[0] << 0x10 | rgb[1] << 0x8 | rgb[2]:06X}`")
        embed.add_field(name="RGB", value=f"`{rgb[0]} {rgb[1]} {rgb[2]}`")
        bgr15 = round(rgb[0] * 0x1F / 0xFF) | round(rgb[1] * 0x1F / 0xFF) << 5 | round(rgb[2] * 0x1F / 0xFF) << 10
        embed.add_field(name="BGR15", value=f"`0x{bgr15:04X}` `0x{bgr15 | 1 << 15:04X}`")
        await ctx.send(embed=embed)

    @commands.command(aliases=["botinfo", "whoisthisbot"])
    async def about(self, ctx):
        embed = discord.Embed(title="About TWLHelper")
        embed.set_author(name="DS-Homebrew")
        embed.url = "https://github.com/DS-Homebrew/TWLHelper"
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/46971470?s=400&v=4")
        embed.description = "TWLHelper, DS⁽ⁱ⁾ Mode Hacking Discord server bot"
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
