#
# ISC License
#
# Copyright (C) 2021-present DS-Homebrew
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# send_dm_message, command_signature, error embeds taken from Kurisu, http://www.apache.org/licenses/LICENSE-2.0
#

import discord
import settings
import traceback
from discord.ext import commands

__all__ = ("send_dm_message",
           "command_signature",
           "create_error_embed",
           "is_staff",
           "check_arg",
           "web_name")


async def send_dm_message(member: discord.Member, message: str, ctx: commands.Context = None, **kwargs) -> bool:
    """A helper function for sending a message to a member's DMs.

    Returns a boolean indicating success of the DM
    and notifies of the failure if ctx is supplied."""
    try:
        await member.send(message, **kwargs)
        return True
    except (discord.HTTPException, discord.Forbidden, discord.NotFound, AttributeError):
        if ctx:
            await ctx.send(f"Failed to send DM message to {member.mention}")
        return False


def command_signature(command, *, prefix=".") -> str:
    """Helper function for a command signature

    Parameters
    -----------
    command: :class:`discord.ext.commands.Command`
        The command to generate a signature for
    prefix: str
        The prefix to include in the signature"""
    signature = f"{discord.utils.escape_markdown(prefix)}{command.qualified_name} {command.signature}"
    return signature


def create_error_embed(ctx, exc) -> discord.Embed:
    embed = discord.Embed(title=f"Unexpected exception in command {ctx.command}", color=0xe50730)
    trace = "".join(traceback.format_exception(etype=None, value=exc, tb=exc.__traceback__))
    embed.description = f'```py\n{trace}```'
    embed.add_field(name="Exception Type", value=exc.__class__.__name__)
    embed.add_field(name="Information", value=f"channel: {ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else 'Direct Message'}\ncommand: {ctx.command}\nmessage: {ctx.message.content}\nauthor: {ctx.author.mention}", inline=False)
    return embed


def is_staff():
    def predicate(ctx):
        return any((role.id in settings.staff_roles or role.name in settings.staff_roles) for role in ctx.message.author.roles) if not ctx.author == ctx.guild.owner else True
    return commands.check(predicate)


def check_arg(argument: str, arg) -> bool:
    """Helper util to check if an argument is in a sequence.

    Returns a boolean indicator if the argument was found in the supplied sequence"""
    if argument.lower() in arg:
        return True
    return False


def web_name(name):
    name = name.lower()
    out = ""
    for letter in name:
        if letter in "abcdefghijklmnopqrstuvwxyz0123456789-_":
            out += letter
        elif letter in ". ":
            out += "-"
    return out
