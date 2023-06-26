from decimal import Decimal, ROUND_UP, getcontext, InvalidOperation

from nextcord import Embed, Interaction, Member, SlashOption, slash_command
from nextcord.ext.commands import Bot, Cog

from database import find_user

bot_collection = [
    "510016054391734273",
    "639599059036012605",
    "726560538145849374",
    "935408554997874798",
]


class Stats(Cog):
    """"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(name="rateup")
    async def rank_up(
        self,
        ctx: Interaction,
        custom_rate: str = SlashOption(
            name="rate",
            description="The rate you want to calculate for",
            required=False,
            default=None,
        ),
    ):
        """Check how many counts are needed to rank up"""
        user = ctx.user
        if not isinstance(user, Member):
            return

        msg = ""
        if custom_rate is not None:
            c_rate = Decimal(custom_rate) / 100
            if c_rate == 1:
                c_rate = Decimal("0.99999")

        og_post = find_user(user.id, bot_collection[0])
        if og_post is not None:
            correct = Decimal(og_post.get("correct", 0))
            wrong = Decimal(og_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`counting`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.000005")
                if custom_rate is not None and c_rate > new_rate:
                    new_rate = c_rate
                try:
                    x = ((new_rate * total - correct) / (1 - new_rate)).quantize(
                        Decimal("1"), ROUND_UP
                    )
                except InvalidOperation:
                    msg += f"\n`counting`: error. What did you type?"
                else:
                    new_cor = correct + x
                    new_rate = (new_rate * 100).quantize(Decimal("10.000"))
                    msg += f"`counting`: Rank up to {new_rate}% at **{new_cor}**. "
                    msg += f"You need ~**{x}** more numbers.\n"

        classic_post = find_user(user.id, bot_collection[1])
        if classic_post is not None:
            correct = Decimal(classic_post.get("correct", 0))
            wrong = Decimal(classic_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`classic`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                getcontext().prec = 8
                new_rate = rate + Decimal("0.000005")
                if custom_rate is not None and c_rate > new_rate:
                    new_rate = c_rate
                try:
                    x = ((new_rate * total - correct) / (1 - new_rate)).quantize(
                        Decimal("1"), ROUND_UP
                    )
                except InvalidOperation:
                    msg += f"\n`classic`: error. What did you type?"
                else:
                    new_cor = correct + x
                    new_rate = (new_rate * 100).quantize(Decimal("10.000"))
                    msg += f"`classic`: Rank up to {new_rate}% at **{new_cor}**. "
                    msg += f"You need ~**{x}** more numbers.\n"

        numselli_post = find_user(user.id, bot_collection[2])
        if numselli_post is not None:
            correct = Decimal(numselli_post.get("correct", 0))
            wrong = Decimal(numselli_post.get("wrong", 0))
            # print(correct, wrong)
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.0000"))
            # print(total, rate)
            if rate >= Decimal("0.9998"):
                msg += "`numselli`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.00005")
                if custom_rate is not None and c_rate > new_rate:
                    new_rate = c_rate
                try:
                    x = ((new_rate * total - correct) / (1 - new_rate)).quantize(
                        Decimal("1"), ROUND_UP
                    )
                except InvalidOperation:
                    msg += f"\n`numselli`: error. What did you type?"
                else:
                    new_cor = correct + x
                    new_rate = (new_rate * 100).quantize(Decimal("10.00"))
                    msg += f"`numselli`: Rank up to {new_rate}% at **{new_cor}**. "
                    msg += f"You need ~**{x}** more numbers.\n"

        crazy_post = find_user(user.id, bot_collection[3])
        if crazy_post is not None:
            correct = Decimal(crazy_post.get("correct", 0))
            wrong = Decimal(crazy_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`classic`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.000005")
                if custom_rate is not None and c_rate > new_rate:
                    new_rate = c_rate
                try:
                    x = ((new_rate * total - correct) / (1 - new_rate)).quantize(
                        Decimal("1"), ROUND_UP
                    )
                except InvalidOperation:
                    msg += f"\n`crazy`: error. What did you type?"
                else:
                    new_cor = correct + x
                    new_rate = (new_rate * 100).quantize(Decimal("10.000"), ROUND_UP)
                    msg += f"`crazy`: Rank up to {new_rate}% at **{new_cor}**. "
                    msg += f"You need ~**{x}** more numbers.\n"

        if msg == "":
            msg = "Run counting commands first!"

        title_msg = f"Rank up stats for {user}"
        embedVar = Embed(title=title_msg, description=msg)
        await ctx.send(embed=embedVar)


def setup(bot: Bot):
    bot.add_cog(Stats(bot))
