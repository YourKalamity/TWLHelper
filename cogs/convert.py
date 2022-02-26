import os
import time
import discord

from aiohttp import client_exceptions
from asyncio.subprocess import create_subprocess_exec
from discord.ext import commands


class Convert(commands.Cog):
    """Used to convert things"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        return True

    def check_dir(self):
        if not os.path.isdir("downloads"):
            os.mkdir("downloads")
        if not os.path.isdir("senpai_converted_downloads"):
            os.mkdir("senpai_converted_downloads")
        return

    async def ffmpeg_img(self, fileName, newFileName, crop=None, pixfmt=None, scale=None):
        command = [
            'ffmpeg',
            '-y',
            '-i',
            fileName,
        ]
        if crop is not None or scale is not None:
            command.append('-vf')
            if crop is not None:
                command.append('crop=' + crop)
            if scale is not None:
                command.append(f"crop='if(gte(ih,iw*3/4),iw,if(gte(iw,ih*4/3),ih*4/3,ih))':'if(gte(ih,iw*3/4),iw*3/4,if(gte(iw,ih*4/3),ih,ih*3/4))',scale={scale}:flags=lanczos")
        if pixfmt is not None:
            command.append('-pix_fmt')
            command.append(pixfmt)
        command.append(newFileName)
        try:
            proc = await create_subprocess_exec(*command)
            await proc.wait()
        except Exception:
            return 1
        return 0

    async def download_media_error(self, ctx, error_num):
        if error_num == 1:
            await ctx.send_help(ctx.command)
        elif error_num == 2:
            await ctx.send("`Error (HTTP error). Try again later.`")
        elif error_num == 3:
            await ctx.send("`Error. Failed to download file.`")
        elif error_num == 4:
            await ctx.send("`Error. Input file size is too large.`")
        elif error_num == 5:
            await ctx.send("`Error. URL invalid.`")

    async def download_media(self, ctx, filelink):
        self.check_dir()
        fileName = None
        if filelink is None:
            if ctx.message.attachments:
                filelink = ctx.message.attachments[0].url
            else:
                return 1
        if filelink:
            file = None
            r = None
            try:
                r = await self.bot.session.get(filelink, allow_redirects=True)
            except client_exceptions.InvalidURL:
                return 5
            if r.status != 200:
                return 2
            if int(r.headers['Content-Length']) >= 104857600:
                return 4
            file = await r.read()
            if filelink.find('/'):
                fileName = f"downloads/{filelink.rsplit('/', 1)[1]}"
            try:
                open(fileName, 'wb').write(file)
            except Exception:
                return 3
        return fileName

    async def convert_img(self, ctx, new_extension="PNG", scale=None, filelink=None, boxart=False):
        start_time = time.time()
        new_extension = new_extension.lower()
        fileName = await self.download_media(ctx, filelink)
        if isinstance(fileName, str):
            async with ctx.typing():
                if boxart or not fileName.endswith('.' + new_extension):
                    outputtext = await ctx.send(f"`Converting to {new_extension.upper()}...`")
                    newFileName = f"senpai_converted_{fileName}_.{new_extension}"
                    pixfmt = "rgb565" if new_extension == "bmp" else None
                    err = await self.ffmpeg_img(fileName, newFileName, scale=scale, pixfmt=pixfmt)
                    if err == 1:
                        return await outputtext.edit(f"`Failed to convert to {new_extension.upper()}`")
                    await outputtext.edit(f"`Converted to {new_extension.upper()}`")
                    await outputtext.edit(f"`Uploading {new_extension.upper()}...`")
                    if os.path.getsize(newFileName) < ctx.guild.filesize_limit:
                        await ctx.send(file=discord.File(newFileName), reference=ctx.message)
                        await outputtext.edit(f"`All done! Completed in {round(time.time() - start_time, 2)} seconds`")
                    else:
                        await outputtext.edit("`Converted image is too large! Cannot send image.`")
                    os.remove(fileName)
                    os.remove(newFileName)
                else:
                    await ctx.send(f"`You asked to convert a {new_extension.upper()} into a ...{new_extension.upper()}?`")
                return
        else:
            await self.download_media_error(ctx, fileName)

    def select_ffmpeg_preset(self, preset_name=None):
        if preset_name == "discord":
            return ["-vcodec", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-profile:v",
                    "baseline", "-level", "3",
                    "-s", "852x480",
                    '-vf', "scale=640:trunc(ow/a/2)*2"]
        elif preset_name == "dsmp4":
            return ['-f', 'mp4',
                    '-vf', "fps=24000/1001, colorspace=space=ycgco:primaries=bt709:trc=bt709:range=pc:iprimaries=bt709:iall=bt709, scale=256:144",
                    '-dst_range', "1",
                    '-color_range', "2",
                    '-vcodec', 'mpeg4',
                    '-profile:v', "0",
                    '-level', "8",
                    "-q:v", "2",
                    "-maxrate", "500k",
                    "-acodec", "aac",
                    "-ar", "32k",
                    "-b:a", "64000",
                    "-ac", "1",
                    "-slices", "1",
                    "-g", "50"]
        elif preset_name is None:
            return []

    def embed(self, title):
        embed = discord.Embed(title=title)
        embed.set_author(name="DS-Homebrew Wiki")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/46971470?s=400&v=4")
        embed.url = "https://wiki.ds-homebrew.com/"
        return embed

    async def convert_vid(self, ctx, new_extension, filelink=None, preset=None, ffmpeg_flags=[]):
        start_time = time.time()
        new_extension = new_extension.lower()
        fileName = await self.download_media(ctx, filelink)
        print(fileName)
        if isinstance(fileName, str):
            async with ctx.typing():
                start_time = time.time()
                size_large = False
                outputtext = await ctx.send("`Converting video...`")
                newFileName = f"downloads/senpai_converted_{time.time()}.{new_extension}"
                command = ['ffmpeg', "-y", '-i', fileName]
                command.extend(self.select_ffmpeg_preset(preset))
                command.extend(ffmpeg_flags)
                command.append(newFileName)
                proc = await create_subprocess_exec(*command)
                await proc.wait()
                await outputtext.edit("`Uploading Video...`")
                if (not isinstance(ctx.channel, discord.channel.DMChannel) and os.path.getsize(newFileName) > ctx.guild.filesize_limit) or isinstance(ctx.channel, discord.channel.DMChannel):
                    size_large = True
                    await outputtext.edit("`Converted video is too large! Cannot send video.`")
                else:
                    await ctx.send(file=discord.File(newFileName), reference=ctx.message)
                os.remove(newFileName)
                os.remove(fileName)
                if not size_large:
                    await outputtext.edit(f"`Done! Completed in {round(time.time() - start_time, 2)} seconds`")
        else:
            await self.download_media_error(ctx, fileName)

    @commands.command(name="unlaunch")
    async def unlaunch_background(self, ctx, *args):
        """
        Convert an attachment or linked image to an Unlaunch GIF file
        Returns the guide on how to create a custom Unlaunch GIF manually if no arguments are provided
        """

        start_time = time.time()
        filelink = next((arg for arg in args if arg.startswith("http")), None)
        fileName = await self.download_media(ctx, filelink)
        if isinstance(fileName, str):
            async with ctx.typing():
                newFileName = f"downloads/senpai_converted_{fileName[10:]}_.gif"
                outputtext = await ctx.send("`Converting to GIF...`")
                try:
                    proc = await create_subprocess_exec("ffmpeg", "-y", "-i", fileName, "-vf", "crop='if(gte(ih,iw*3/4),iw,if(gte(iw,ih*4/3),ih*4/3,ih))':'if(gte(ih,iw*3/4),iw*3/4,if(gte(iw,ih*4/3),ih,ih*3/4))',scale=256:192:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse", "-frames", "1", newFileName)
                    await proc.wait()
                except Exception:
                    return await outputtext.edit("`Failed to convert to GIF`")
                await outputtext.edit("`Converted to GIF...`")
                await outputtext.edit("`Colour Mapping GIF...`")
                try:
                    gifsicle_args = ["gifsicle", newFileName, "-O3", "--no-extensions", "-k31", "#0", "-o", newFileName]
                    if "-dither" in args:
                        gifsicle_args.append("-f")
                    proc = await create_subprocess_exec(*gifsicle_args)
                    await proc.wait()
                except Exception:
                    return await outputtext.edit("`Failed to map GIF colour...`")
                await outputtext.edit("`GIF colour mapped...`")
                await outputtext.edit("`Optimising GIF size...`")
                x = 0
                while x <= 300 and os.stat(newFileName).st_size > 15000:
                    proc = await create_subprocess_exec("gifsicle", newFileName, "-O3", "--no-extensions", f"--lossy={x}", "-k31", "-o", newFileName)
                    await proc.wait()
                    x += 50
                warning = os.stat(newFileName).st_size > 15000
                await outputtext.edit("`GIF size optimised`")
                await outputtext.edit("`Uploading GIF...`")
                await ctx.send(file=discord.File(newFileName), reference=ctx.message)
                os.remove(fileName)
                os.remove(newFileName)
                await outputtext.edit(f"`All done! Completed in {round(time.time() - start_time, 2)} seconds`")
                if warning:
                    await ctx.send("`[Warning] : File size was not reduced to less than 15KiB.\n[Warning] : Converted GIF won't work with Unlaunch (try something less complicated)`")
                return
        elif fileName == 1:
            embed = self.embed("Custom Unlaunch Backgrounds")
            embed.url += "twilightmenu/custom-unlaunch-backgrounds.html"
            embed.description = "How to make custom Unlaunch backgrounds and install them using TWiLight Menu++"
            return await ctx.send(embed=embed)
        else:
            await self.download_media_error(ctx, fileName)

    @commands.command()
    async def bmp(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to BMP
        """
        await self.convert_img(ctx, "bmp", filelink=filelink)

    @commands.command()
    async def png(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to PNG
        """
        await self.convert_img(ctx, "png", filelink=filelink)

    @commands.command(aliases=["jpg"])
    async def jpeg(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to JPEG
        """
        await self.convert_img(ctx, "jpeg", filelink=filelink)

    @commands.command()
    async def gif(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to GIF
        """
        start_time = time.time()
        fileName = await self.download_media(ctx, filelink)
        if isinstance(fileName, str):
            async with ctx.typing():
                outputtext = await ctx.send("`Image downloaded...`")
                if not fileName.endswith('.gif'):
                    await outputtext.edit("`Converting to GIF...`")
                    newFileName = f"senpai_converted_{fileName}_.gif"
                    try:
                        proc = await create_subprocess_exec("ffmpeg", "-y", "-i", fileName, "-vf", "palettegen", "downloads/palette.png")
                        await proc.wait()
                        proc = await create_subprocess_exec("ffmpeg", "-y", "-i", fileName, "-i", "downloads/palette.png", "-filter_complex", "paletteuse", newFileName)
                        await proc.wait()
                    except Exception:
                        return await outputtext.edit("`Failed to convert to GIF`")
                    await outputtext.edit("`Converted to GIF`")
                    await outputtext.edit("`Uploading GIF...`")
                    if os.path.getsize(newFileName) < ctx.guild.filesize_limit:
                        await ctx.send(file=discord.File(newFileName), reference=ctx.message)
                        await outputtext.edit(f"`All done! Completed in {round(time.time() - start_time, 2)} seconds`")
                    else:
                        await outputtext.edit("`Converted GIF is too large! Cannot send GIF.`")
                    os.remove(fileName)
                    os.remove(newFileName)
                    os.remove("downloads/palette.png")
                    return
                else:
                    return await outputtext.edit("`You asked me to convert a GIF into a ... GIF`")
        else:
            await self.download_media_error(ctx, fileName)

    @commands.group()
    async def boxart(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = self.embed("How to Get Box Art")
            embed.url += "twilightmenu/how-to-get-box-art.html"
            embed.description = "How to add box art to TWiLight Menu++"
            await ctx.send(embed=embed)

    @boxart.command(name="nds", aliases=["dsi"])
    async def ds_boxart(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to a DS Box Art
        """
        await self.convert_img(ctx, scale="128:115", filelink=filelink, boxart=True)

    @boxart.command(name="gba", aliases=["fds", "gbc", "gb"])
    async def gba_boxart(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to a GB, GBC, GBA or FDS Box Art
        """
        await self.convert_img(ctx, scale="115:115", filelink=filelink, boxart=True)

    @boxart.command(name="nes", aliases=["gen", "md", "sfc", "ms", "gg"])
    async def nes_boxart(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to a NES, Super Famicom, GameGear, Master System, Mega Drive or Genesis Box Art
        """
        await self.convert_img(ctx, scale="84:115", filelink=filelink, boxart=True)

    @boxart.command(name="snes")
    async def snes_boxart(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to an SNES Box Art
        """
        await self.convert_img(ctx, scale="158:115", filelink=filelink, boxart=True)

    @commands.command()
    async def dsimenu(self, ctx, filelink=None):
        """
        Converts an attached, or linked, image to a TWLMenu++ DSi Menu Theme
        """
        await self.convert_img(ctx, scale="208:156", filelink=filelink, boxart=True)

    @commands.command()
    async def dsmp4(self, ctx, filelink=None):
        """
        Converts an attached, or linked, video to a DSi Video for MPEG4 Player
        """
        await self.convert_vid(ctx, "mp4", filelink, "dsmp4")

    @commands.command(aliases=["mp4"])
    async def video(self, ctx, filelink=None):
        """
        Converts an attached, or linked, video to MP4
        """
        await self.convert_vid(ctx, "mp4", filelink, "discord")

    @commands.command(aliases=["bgm"])
    async def twlbgm(self, ctx, filelink=None):
        """
        Converts an attached, or linked, audio file to TWiLight Menu's BGM format
        Returns the guide on how to add and create custom audio files for TWiLight Menu if no arguments are provided
        """

        fileName = await self.download_media(ctx, filelink)
        if isinstance(fileName, str):
            async with ctx.typing():
                start_time = time.time()
                failed = False
                outputtext = await ctx.send("`Converting audio...`")
                proc = await create_subprocess_exec("ffmpeg", "-y", "-i", fileName, "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16k", "downloads/bgm.pcm.raw")
                await proc.wait()

                await outputtext.edit("`Uploading BGM...`")
                if not os.path.exists("downloads/bgm.pcm.raw"):
                    failed = True
                    await outputtext.edit("`Conversion failed. Is the attachment an audio stream?`")
                elif (not isinstance(ctx.channel, discord.channel.DMChannel) and os.path.getsize("downloads/bgm.pcm.raw") > ctx.guild.filesize_limit) or isinstance(ctx.channel, discord.channel.DMChannel):
                    failed = True
                    await outputtext.edit("`Converted BGM is too large! Cannot send BGM.`")
                else:
                    await ctx.send(file=discord.File("downloads/bgm.pcm.raw"), reference=ctx.message)
                for target in ("downloads/bgm.pcm.raw", fileName):
                    try:
                        os.remove(target)
                    except FileNotFoundError:
                        pass
                if not failed:
                    await outputtext.edit(f"`All done! Completed in {round(time.time() - start_time, 2)} seconds`")
        elif fileName == 1:
            embed = self.embed("DSi/3DS Skins - Custom SFX")
            embed.url += "twilightmenu/custom-dsi-3ds-sfx.html"
            embed.description = "How to use custom background music and sound effects in DSi and 3DS skins for TWiLight Menu++"
            return await ctx.send(embed=embed)
        else:
            await self.download_media_error(ctx, fileName)


def setup(bot):
    bot.add_cog(Convert(bot))
