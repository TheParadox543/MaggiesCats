import json
from pprint import PrettyPrinter
from re import findall, match, search

from nextcord import (
    Embed,
    Guild,
    Interaction,
    Member,
    Message,
    Permissions,
    Role,
    SlashOption,
    slash_command,
)
from nextcord.ext.commands import Bot, Cog, Context, command, is_owner
from nextcord.utils import get

DUCK_BOT = 510016054391734273
NUMSELLI_BOT = 726560538145849374
CRAZY_BOT = 935408554997874798
pp = PrettyPrinter(indent=4)


def read_settings():
    content = {
        "duck": {
            "id": DUCK_BOT,
        },
        "numselli": {
            "id": NUMSELLI_BOT,
        },
        "crazy": {
            "id": CRAZY_BOT,
        },
    }
    try:
        with open("bot_settings.json", "r") as settings:
            try:
                content: dict[str, dict[str, int]] = json.load(settings)
            except json.decoder.JSONDecodeError:
                pass
    except FileNotFoundError:
        pass
    return content


async def give_count_permission(
    saves: int,
    accuracy: int,
    counter: Member,
    guild: Guild,
    message: Message,
    bot: str,
):
    """Giving permission to count in respective bots"""

    content = read_settings()
    bot_id = content[bot]["id"]
    accuracy_set = content[bot].get("accuracy", 99)
    role_id = content[bot].get("role", None)
    if role_id is None:
        await message.channel.send(f"Role not set for <@{bot_id}>")
        return
    role = guild.get_role(role_id)
    if role is None:
        await message.channel.send(f"Role could not be found")
        return
    if saves >= 1 and accuracy >= accuracy_set:
        if role in counter.roles:
            reaction = get(
                guild.emojis,
                name="icecheckmark",
            )
            if reaction is not None:
                await message.add_reaction(reaction)
        else:
            await counter.add_roles(
                role,
                reason="Meets criteria",
            )
            await message.channel.send(
                f"{counter.mention} can now count with <@{bot_id}>."
            )
    else:
        if role in counter.roles:
            await counter.remove_roles(
                role,
                reason="Doesn't satisfy criteria",
            )
            await message.channel.send(
                f"{counter.mention} can't count with <@{bot_id}>."
            )
        else:
            reaction = get(guild.emojis, name="warncount")
            if reaction is not None:
                await message.add_reaction(reaction)


def counting_check(m: Message):
    return m.author.id == DUCK_BOT


class Monitor(Cog):
    """Monitor the different bots and give permissions"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        """Deal with messages"""
        if not isinstance(message.author, Member):
            return
        if not isinstance(message.guild, Guild):
            return

        # * c!user
        if message.content.startswith("c!user"):
            msg = await self.bot.wait_for("message", check=counting_check)
            if not isinstance(msg, Message):
                return
            if len(msg.embeds) != 1:
                return

            numbers = findall("\d+", message.content)  # type: ignore
            if len(numbers) == 1:
                user_id = int(numbers[0])
            else:
                user_id = message.author.id

            embed_content = msg.embeds[0].to_dict()
            user = message.guild.get_member(user_id)
            if user is None:
                return
            if "fields" not in embed_content:
                return
            embed_field = embed_content["fields"][0]
            field_value = embed_field["value"]
            accuracy = int(findall("\d+", field_value)[0])  # type: ignore
            saves_str = field_value.split("Saves: ")[1]
            saves = int(findall("\d", saves_str)[0])  # type: ignore
            await give_count_permission(
                saves,
                accuracy,
                user,
                message.guild,
                msg,
                "duck",
            )

        # * Numselli
        elif message.author.id == NUMSELLI_BOT and len(message.embeds) == 1:
            embed_content = message.embeds[0].to_dict()
            embed_title = embed_content.get("title")
            if embed_title is None:
                return

            # * Numselli user
            if embed_title.startswith("Stats"):
                user_name = embed_title.split("Stats for ")[1]
                if user_name is None:
                    return
                user = message.guild.get_member_named(user_name)
                if user is None:
                    return
                if "fields" not in embed_content:
                    return
                embed_field = embed_content["fields"][0]
                field_value = embed_field["value"]
                accuracy = int(findall("\d+", field_value)[0])  # type: ignore
                saves_str = field_value.split("Saves left: ")[1]
                saves = int(findall("\d", saves_str)[0])  # type: ignore
                await give_count_permission(
                    saves,
                    accuracy,
                    user,
                    message.guild,
                    message,
                    "numselli",
                )

            # * Numselli error
            elif embed_title.startswith("Save Used"):
                embed_description = embed_content.get("description")
                if embed_description is None:
                    await message.channel.send("Could not read embed")
                    return
                numbers = findall("\d+", embed_description)  # type: ignore
                user_id = int(numbers[0])
                saves = int(numbers[1])
                user = message.guild.get_member(user_id)
                if user is None:
                    await message.channel.send("Could not identify the user")
                    return
                await give_count_permission(
                    saves,
                    99,
                    user,
                    message.guild,
                    message,
                    "numselli",
                )

        # * Crazy Counting user
        elif message.author.id == CRAZY_BOT and len(message.embeds) == 1:
            embed_content = message.embeds[0].to_dict()
            embed_title = embed_content.get("title")
            if embed_title is None:
                return
            if embed_title.startswith("Stats"):
                user_name = embed_title.split("Stats for ")[1]
                if user_name is None:
                    return
                user = message.guild.get_member_named(user_name.split("#")[0])
                if user is None:
                    return
                if "fields" not in embed_content:
                    return
                embed_field = embed_content["fields"][0]
                field_value = embed_field["value"]
                accuracy = int(findall("\d+", field_value)[0])  # type: ignore
                saves_str = field_value.split("Saves: ")[1]
                saves = int(findall("\d", saves_str)[0])  # type: ignore
                await give_count_permission(
                    saves,
                    accuracy,
                    user,
                    message.guild,
                    message,
                    "crazy",
                )

        # * Error from counting
        if (
            message.author.id == DUCK_BOT
            and message.content is not None
            and len(message.embeds) == 0
            and "You have" in message.content
        ):
            content = message.content
            numbers = findall("\d+", content)  # type: ignore
            user_id = int(numbers[0])
            user = message.guild.get_member(user_id)
            if user is None:
                await message.channel.send("Couldn't find who made the mistake")
                return
            if "your saves" in content:
                saves = int(numbers[2])
            else:
                saves = 0
            await give_count_permission(
                saves,
                99,
                user,
                message.guild,
                message,
                "duck",
            )

        # * Error from crazy counting
        if (
            message.author.id == CRAZY_BOT
            and message.content is not None
            and len(message.embeds) == 0
            and "has used a" in message.content
        ):
            content = message.content
            numbers = findall("\d+", content)  # type: ignore
            user_id = int(numbers[0])
            user = message.guild.get_member(user_id)
            if user is None:
                await message.channel.send("Couldn't find who made the mistake")
                return
            if "has used a save" in content:
                saves = int(numbers[1])
            elif "has used a channel save" in content:
                saves = 0
            else:
                return
            await give_count_permission(
                saves,
                99,
                user,
                message.guild,
                message,
                "crazy",
            )

    @command(name="clear")
    @is_owner()
    async def remove_roles(self, ctx: Context, role: Role):
        """Remove all users from the role"""
        for member in role.members:
            await member.remove_roles(role, reason="Clearing roles from users")
            await ctx.send(f"{role} removed from {member.name}")

    @slash_command(
        default_member_permissions=Permissions(manage_guild=True),
    )
    async def botsettings(self, ctx):
        return

    @botsettings.subcommand(
        name="set",
        description="Set the requirements for each bot",
    )
    async def set(
        self,
        ctx: Interaction,
        bot: str = SlashOption(
            name="bot",
            description="The bot",
            choices=[
                "duck",
                "numselli",
                "crazy",
            ],
            required=True,
        ),
        role: Role | None = None,
        accuracy: int | None = None,
    ):
        """Set the requirements to count for each bot"""
        content = read_settings()
        with open("bot_settings.json", "w+") as settings:
            bot_data = content[bot]
            if role is not None:
                bot_data["role"] = role.id
            if accuracy is not None:
                bot_data["accuracy"] = accuracy
            content[bot] = bot_data
            json.dump(content, settings, indent=4)
        description = f"Bot: <@{bot_data['id']}>"
        if bot_data.get("role"):
            description += f"\nRole: <@&{bot_data['role']}>"
        if bot_data.get("accuracy"):
            description += f"\nAccuracy: {bot_data['accuracy']}"
        embedVar = Embed(title=bot, description=description)
        await ctx.send(embed=embedVar)

    @botsettings.subcommand()
    async def view(
        self,
        ctx: Interaction,
        bot: str = SlashOption(
            description="The bot to be checked",
            choices=[
                "duck",
                "numselli",
                "crazy",
            ],
        ),
    ):
        """Check the settings"""
        content = read_settings()
        bot_data = content[bot]
        description = f"Bot: <@{bot_data['id']}>"
        if bot_data.get("role"):
            description += f"\nRole: <@&{bot_data['role']}>"
        if bot_data.get("accuracy"):
            description += f"\nAccuracy: {bot_data['accuracy']}"
        embedVar = Embed(title=bot, description=description)
        await ctx.send(embed=embedVar)


def setup(bot: Bot):
    bot.add_cog(Monitor(bot))
