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

from database import update_user

DUCK_BOT = 510016054391734273
CLASSIC_BOT = 639599059036012605
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


def name_extractor(title: str):
    """Extract the user name from the title"""

    if "Stats" in title:
        title = title.split("Stats for ")[1]
    #     return name.split("#")[0]
    # else:
    return title.split("#")[0]


def stats_embed_extractor(embed: Embed):
    """Extract the numbers from an embed"""

    embed_content = embed.to_dict()
    if "fields" not in embed_content:
        return None, None
    if "Stats" not in embed_content["fields"][0]["name"]:
        return None, None

    user_name = None
    if "title" in embed_content:
        user_name = name_extractor(embed_content["title"])
    elif "author" in embed_content:
        if "name" in embed_content["author"]:
            user_name = embed_content["author"]["name"]

    field_content = embed_content["fields"][0]["value"].replace(",", "")
    numbers_list: list[str] = findall("[\d\.]+", field_content)
    numbers_return = (
        float(numbers_list[0]),
        int(numbers_list[1]),
        int(numbers_list[2]),
    )
    if "Saves" in field_content:
        saves_str = field_content.split("Saves")[1]
        saves = int(findall("\d+", saves_str)[0])
        numbers_return = numbers_return + (saves,)
    return user_name, numbers_return


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
                user = message.guild.get_member(user_id)
            else:
                user = message.author

            user_name, numbers_list = stats_embed_extractor(msg.embeds[0])
            if user is None:
                return
            if numbers_list is None:
                return
            saves = numbers_list[-1]
            update_user(
                message.author,
                *numbers_list[0:3],
                msg.author.id,
            )
            await give_count_permission(
                numbers_list[-1],
                int(numbers_list[0]),
                user,
                message.guild,
                msg,
                "duck",
            )

        # * classic bot
        elif message.author.id == CLASSIC_BOT and len(message.embeds) == 1:
            user_name, numbers_list = stats_embed_extractor(message.embeds[0])
            if user_name is None:
                await message.channel.send("Could not find user name")
                return
            if numbers_list is None:
                await message.channel.send("Could not read the field")
                return
            user = message.guild.get_member_named(user_name)
            if user is None:
                return
            update_user(
                user,
                *numbers_list[0:3],
                message.author.id,
            )

        # * Numselli
        elif message.author.id == NUMSELLI_BOT and len(message.embeds) == 1:
            embed_content = message.embeds[0].to_dict()
            embed_title = embed_content.get("title")
            if embed_title is None:
                return

            # * Numselli user
            if embed_title.startswith("Stats"):
                user_name, numbers_list = stats_embed_extractor(message.embeds[0])
                if user_name is None:
                    await message.channel.send("Could not find the user")
                    return
                if numbers_list is None:
                    await message.channel.send("Could not read the field")
                    return
                user = message.guild.get_member_named(user_name)
                if user is None:
                    return
                update_user(
                    user,
                    *numbers_list[0:3],
                    message.author.id,
                )
                await give_count_permission(
                    numbers_list[-1],
                    int(numbers_list[0]),
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
            user_name, numbers_list = stats_embed_extractor(message.embeds[0])
            if numbers_list is None:
                await message.channel.send("Could not read field")
                return
            if user_name is None:
                return
            user = message.guild.get_member_named(user_name.split("#")[0])
            if user is None:
                return
            update_user(
                user,
                *numbers_list[0:3],
                message.author.id,
            )
            await give_count_permission(
                numbers_list[-1],
                int(numbers_list[0]),
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
