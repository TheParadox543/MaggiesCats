from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from certifi import where

from nextcord import Member

load_dotenv()
ca = where()

client = MongoClient(getenv("DB_LOCAL_TOKEN"), tlsCAFile=ca)
# client = MongoClient(getenv("DB_USA_TOKEN"), tlsCAFile=ca)

db = client["maggie"]
classic_collection = db["classic_collection"]
duck_collection = db["duck_collection"]
numselli_collection = db["numselli_collection"]
crazy_collection = db["crazy_collection"]

bot_collection = {
    "510016054391734273": duck_collection,
    "639599059036012605": classic_collection,
    "726560538145849374": numselli_collection,
    "935408554997874798": crazy_collection,
}


def update_user(
    user: Member,
    rate: float,
    correct: int,
    wrong: int,
    bot: int | str,
):
    """Update the data of a user

    Parameters
    -----------
        user (Member): The user whose stats is available
        rate (float): The rate of correct
        correct (int): The number of correct counts
        wrong (int): The number of wrong counts
        bot (int | str): The bot who gave the stats
    """

    result = bot_collection[f"{bot}"].update_one(
        {
            "_id": f"{user.id}",
        },
        {
            "$set": {
                "name": f"{user.display_name}",
                "correct": correct,
                "wrong": wrong,
                "rate": rate,
            },
        },
        True,
    )
    return result.modified_count


def find_user(user_id: int, bot: int | str):
    """Find user data

    Parameters
    ----------
        user_id (int): The ID of the user
        bot (int | str): The bot who gave the stats

    Returns
    -------
    """

    return bot_collection[f"{bot}"].find_one({"_id": f"{user_id}"})
