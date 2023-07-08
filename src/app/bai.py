from datetime import datetime
from enum import auto, StrEnum
import re

from requests_cache import CachedSession

from urllib.parse import quote
from urllib.request import urlopen

import pandas as pd
import matplotlib.pyplot as plt


plt.rcParams["figure.figsize"] = (10, 10)


class Preset(StrEnum):
    duel = auto()
    team = auto()
    ffa = auto()
    all = auto()


# Cache the data
def get_data(url: str):
    # print(f"Getting data from {url}")
    session = CachedSession("bar_cache", backend="sqlite")
    data = session.get(url).json()
    return data


# Get user name from user id
def get_user_name(user_id: int):
    name_list = get_data("https://api.bar-rts.com/cached-users")
    user_name = ""
    for user in name_list:
        if user["id"] == user_id:
            user_name = user["username"]
    return user_name


def get_user_id(user_name: str):
    name_list = get_data("https://api.bar-rts.com/cached-users")
    user_id = ""
    for user in name_list:
        if user["username"] == user_name:
            user_id = user["id"]
    return user_id


def process_match_data(match_details_df):
    if match_details_df.empty:
        return match_details_df
    # Get the winning team and count the number of wins
    match = {}
    matches = []

    for _, game in match_details_df.iterrows():
        # print(game)
        for team in game["AllyTeams"]:
            for player in team["Players"]:
                match = {
                    **match,
                    **{
                        "id": team["id"],
                        "userId": player["userId"],
                        "teamId": player["teamId"],
                        "allyTeamId": player["allyTeamId"],
                        "name": player["name"],
                        "faction": player["faction"],
                        "rank": player["rank"],
                        "skillUncertainty": player["skillUncertainty"],
                        "skill": float(re.sub("[^0123456789\.]", "", player["skill"])),
                        "startPos": player["startPos"],
                        "winningTeam": team["winningTeam"],
                        "Map.fileName": game["Map.fileName"]
                        + "_"
                        + str(len(team["Players"]))
                        + "v"
                        + str(len(team["Players"])),
                        "Map.scriptName": game["Map.scriptName"],
                        "durationMs": game["durationMs"],
                        "startTime": game["startTime"],
                    },
                }
                matches.append(match)

    matches_df = pd.json_normalize(matches)
    matches_df["startTime"] = pd.to_datetime(matches_df["startTime"])
    return matches_df


# Get match details for each match
def get_match_details(id: str):
    match_details = get_data(f"https://api.bar-rts.com/replays/{id}")

    match_details_df = pd.json_normalize(match_details)
    match_details_df["startTime"] = pd.to_datetime(match_details_df["startTime"])
    return match_details_df


# Get the players replays metadata
def get_match_data(
    matches_bar,
    user: str,
    preset: Preset = Preset.team,
    season0: bool = False,
):
    # Depending on the preset, the API returns different data.json
    # The preset uses the following format: &preset=duel%2Cffa%2Cteam
    # duel%2Cffa%2Cteam is the same as duel,ffa,team

    if preset == Preset.all:
        preset = "&preset=duel&preset=ffa&preset=team"
    else:
        preset = f"&preset={preset.name}"

    # If season0 is true, then only get games after June 1st, 2023 %2C
    date_range = ""
    if season0:
        date_range = f"&date=2023-06-01&date={datetime.today().strftime('%Y-%m-%d')}"

    uri = f"https://api.bar-rts.com/replays?page=1&limit=9999{preset}{date_range}&hasBots=false&endedNormally=true&players="

    data = get_data(f"{uri}{quote(user)}")

    # Test data has attribute data
    # if not hasattr(data, "data"):
    #     return pd.DataFrame()

    # Get the winning team and count the number of wins
    matches = []
    percent_complete = 0
    number_of_matches = len(data["data"])
    for index, game in enumerate(data["data"]):
        percent_complete += 1
        matches_bar.progress(
            percent_complete / number_of_matches,
            text=f"Getting API for game {index+1} out of {number_of_matches} games. ({game['id']})",
        )
        if game["Map"]["fileName"] is not None:
            matches.append(get_match_details(game["id"]))

    if len(matches) == 0:
        return pd.DataFrame()

    matches_df = pd.concat(matches, axis=0)
    return matches_df


# Get the win rate for each map
def get_win_rate(
    df,
    user: str,
    min_games: int = 5,
):
    if df.empty:
        return df

    user_id = get_user_id(user)
    if user_id == "":
        print(f"{user} does not exist")
        return pd.DataFrame()

    win_rate = (
        df.query(f"userId == {user_id}")
        .groupby(["Map.fileName"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        .query(f"count >= {str(min_games)}")
        .sort_values([("mean"), ("count")], ascending=True)
    )
    return win_rate


def get_fractions_win_rate(df, user: str):
    return (
        df.query(f"userId == {get_user_id(user)}")
        .groupby(["faction"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        # .query(f"count > {str(5)}")
        # .sort_values([("mean"), ("count")], ascending=True)
    )


def get_best_teammates(df, user: str, min_games: int = 5):
    team_winrate = (
        df.groupby(  # .query(f"userId == {get_user_id('furyhawk')}")
            ["allyTeamId", "userId"]
        ).agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        # .query(f"count > {str(1)}")
        # .sort_values([("mean"), ("count")], ascending=True)
    )

    # From team_winrate, get the allyTeamId of the user
    team_ally_id = team_winrate.query(f"userId == {get_user_id(user)}").index.unique(
        level="allyTeamId"
    )
    teams_df = df[df["allyTeamId"].isin(team_ally_id)]
    best_teammates_df = (
        teams_df.groupby(["name", "userId"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        .query(f"count >= {str(min_games)} & userId != {get_user_id(user)}")
        .sort_values([("mean"), ("count")], ascending=False)
    )
    return best_teammates_df
