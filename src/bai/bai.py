from datetime import datetime
from enum import auto, StrEnum
import re
from typing import Any, List, Literal
from matplotlib.figure import Figure

from requests_cache import CachedSession

from urllib.parse import quote

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from streamlit.delta_generator import DeltaGenerator

plt.rcParams["figure.figsize"] = (10, 10)


class Preset(StrEnum):
    duel = auto()
    team = auto()
    ffa = auto()
    all = auto()


def get_data(url: str):
    """Get data from the API and cache it"""
    # print(f"Getting data from {url}")
    session = CachedSession("bar_cache", backend="sqlite", expire_after=259200)
    data = session.get(url).json()
    return data


def get_fresh_data(url: str):
    """Get data from the API and cache it for 60 seconds"""
    # print(f"Getting data from {url}")
    session = CachedSession("short_cache", backend="sqlite", expire_after=60)
    data = session.get(url).json()
    return data


def get_user_name(user_id: int) -> Any | Literal[""]:
    """Get the user name from the user id"""
    name_list = get_data("https://api.bar-rts.com/cached-users")
    user_name = ""
    for user in name_list:
        if user["id"] == user_id:
            user_name = user["username"]
    return user_name


def get_user_id(user_name: str) -> Any | Literal[""]:
    """Get the user id from the user name"""
    name_list = get_data("https://api.bar-rts.com/cached-users")
    user_id = ""
    for user in name_list:
        if user["username"] == user_name:
            user_id = user["id"]
    print(f"User id is {user_id}: {user_name}")
    return user_id


def process_match_data(match_details_df: pd.DataFrame) -> pd.DataFrame:
    """Process the match data into a dataframe"""
    if match_details_df.empty:
        return match_details_df
    # Get the winning team and count the number of wins
    match = {}
    matches: List[Any] = []

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
                        "skill": float(re.sub(r"[^0123456789.]", "", player["skill"]))
                        if player["skill"] is not None
                        else 0.0,
                        "startPos": player["startPos"],
                        "winningTeam": team["winningTeam"],
                        "Map.fileName": game["Map.fileName"],
                        # + "_"
                        # + str(len(team["Players"]))
                        # + "v"
                        # + str(len(team["Players"])),
                        "Map.scriptName": game["Map.scriptName"],
                        "durationMs": game["durationMs"],
                        "startTime": game["startTime"],
                    },
                }
                matches.append(match)

    matches_df: pd.DataFrame = pd.json_normalize(matches)
    matches_df["startTime"] = pd.to_datetime(matches_df["startTime"])
    return matches_df


def get_match_details(id: str) -> pd.DataFrame:
    """Get the match details for a specific match"""
    match_details = get_data(f"https://api.bar-rts.com/replays/{id}")

    match_details_df: pd.DataFrame = pd.json_normalize(match_details)
    match_details_df["startTime"] = pd.to_datetime(match_details_df["startTime"])
    return match_details_df


# Get the players replays metadata
def get_match_data(
    matches_bar: DeltaGenerator,
    user: str,
    preset: Preset = Preset.team,
    season0: bool = True,
) -> pd.DataFrame:
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

    data = get_fresh_data(f"{uri}{quote(user)}")

    # Test data has attribute data
    # if not hasattr(data, "data"):
    #     raise ValueError(f"User {user} has no data")

    # Get the winning team and count the number of wins
    matches: List[Any] = []
    percent_complete = 0
    number_of_matches: int = len(data["data"])
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

    matches_df: pd.DataFrame = pd.concat(matches, axis=0)
    return matches_df


# Get the players replays metadata
def get_quick_match_data(
    user: str,
    preset: Preset = Preset.team,
    season0: bool = True,
) -> pd.DataFrame:
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

    uri: str = f"https://api.bar-rts.com/replays?page=1&limit=9999{preset}{date_range}&hasBots=false&endedNormally=true&players="

    data = get_fresh_data(f"{uri}{quote(user)}")

    # Get the winning team and count the number of wins
    match = {}
    matches: List[Any] = []

    for game in data["data"]:
        if game["Map"]["fileName"] is not None:
            # print(game["id"])
            for team in game["AllyTeams"]:
                for player in team["Players"]:
                    if player["name"] == user:
                        match = {
                            **match,
                            **{
                                "id": game["id"],
                                "name": player["name"],
                                "winningTeam": team["winningTeam"],
                                "Map.fileName": game["Map"]["fileName"],
                                "Map.scriptName": game["Map"]["scriptName"],
                                "durationMs": game["durationMs"],
                                "startTime": game["startTime"],
                            },
                        }
                        matches.append(match)

    matches_df: pd.DataFrame = pd.json_normalize(matches)
    # matches_df["startTime"] = pd.to_datetime(matches_df["startTime"])
    return matches_df


def get_win_rate(
    df: pd.DataFrame,
    user: str,
    min_games: int = 5,
) -> pd.DataFrame:
    """Get the win rate for each map"""
    if df.empty:
        return df

    user_id = get_user_id(user)
    if user_id == "":
        print(f"{user} does not exist")
        return pd.DataFrame()

    # get top 10 meand and count of games for each map
    win_rate_df: pd.DataFrame = (
        df.query(f"userId == {user_id}")
        .groupby(["Map.fileName"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        .query(f"count >= {str(min_games)}")
        .sort_values([("mean"), ("count")], ascending=True)
    )
    return win_rate_df


def get_quick_win_rate(
    df: pd.DataFrame,
    min_games: int = 5,
) -> pd.DataFrame:
    """Get the win rate for each map"""
    if df.empty:
        return df

    # get top 10 mean and count of games for each map
    win_rate_df: pd.DataFrame = (
        df.groupby(["Map.fileName"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        .query(f"count >= {str(min_games)}")
        .sort_values([("mean"), ("count")], ascending=True)
    )
    return win_rate_df


def get_fractions_win_rate(df: pd.DataFrame, user: str) -> pd.Series:
    return (
        df.query(f"userId == {get_user_id(user)}")
        .groupby(["faction"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
    )


def get_best_teammates(df: pd.DataFrame, user: str, min_games: int = 5) -> pd.DataFrame:
    team_winrate = df.groupby(["allyTeamId", "userId"]).agg(
        {"winningTeam": ["mean", "count"]}
    )["winningTeam"]

    # From team_winrate, get the allyTeamId of the user
    team_ally_id = team_winrate.query(f"userId == {get_user_id(user)}").index.unique(
        level="allyTeamId"
    )
    teams_df: pd.DataFrame = df[df["allyTeamId"].isin(team_ally_id)]
    best_teammates_df: pd.DataFrame = (
        teams_df.groupby(["name", "userId"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        .query(f"count >= {str(min_games)} & userId != {get_user_id(user)}")
        .sort_values([("mean"), ("count")], ascending=False)
    )
    return best_teammates_df


def get_battle_list() -> pd.DataFrame:
    """Get the list of battles"""
    battles_json = get_fresh_data("https://api.bar-rts.com/battles")
    return pd.json_normalize(battles_json)


def get_battle_details(battles_df: pd.DataFrame) -> pd.DataFrame:
    """Get the details of the best battle"""
    battle_list: List[Any] = []

    best_battle = battles_df.head(1)  # Get the first battle
    for players in best_battle["players"]:
        for player in players:
            if "teamId" in player and "gameStatus" in player:  # skill userId
                battle_list.append(
                    {
                        "teamId": player["teamId"],
                        "username": player["username"],
                        "userId": player["userId"],
                        "skill": float(re.sub(r"[^0123456789.]", "", player["skill"]))
                        if player["skill"] is not None
                        else 0.0,
                        "gameStatus": player["gameStatus"],
                        "map": best_battle["mapFileName"].values[0],
                        "title": best_battle["title"].values[0],
                    }
                )

    return pd.DataFrame(battle_list).sort_values(by="teamId")


def get_map_win_rate(win_rate_user_df: pd.DataFrame, map_name: str) -> pd.DataFrame:
    """Get the win rate for a specific map"""
    if win_rate_user_df.empty:
        return win_rate_user_df
    df = win_rate_user_df.reset_index()
    map_win_rate_df = df.loc[df["Map.fileName"] == map_name]
    return map_win_rate_df


# Set the x axis minor locator to 5 and major locator to 10
# Set the y axis to the map name
def plot_win_rate(
    win_rate_df: pd.DataFrame,
    user: str,
    preset: Preset = Preset.team,
) -> Figure:
    """Plot the win rate for each map"""
    # Get overall win rate
    overall_win_rate: float = win_rate_df["mean"].mean()
    # Get total number of games
    total_games: int = win_rate_df["count"].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey="all", figsize=(12, 6))

    bars = ax1.barh(
        y=win_rate_df.index,
        width=win_rate_df["mean"],
        alpha=0.75,
    )
    ax1.bar_label(bars, fmt="{:.0%}", label_type="center")
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.05))
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    ax1.grid(which="minor", axis="x", linestyle="--")
    ax1.grid(which="major", axis="x", linestyle="-")
    ax1.set_xlabel("Winning %")
    ax1.set_ylabel("Map")
    ax1.set_xlim(0, 1)
    ax1.set_title(f"{user} winning {preset.name} games @ {overall_win_rate:.0%}")

    ax1.set_axisbelow(True)

    bars = ax2.barh(
        y=win_rate_df.index,
        width=win_rate_df["count"],
        alpha=0.75,
    )

    ax2.bar_label(bars, label_type="center")
    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax2.grid(which="minor", axis="x", linestyle="--")
    ax2.grid(which="major", axis="x", linestyle="-")
    ax2.set_xlabel("Games")
    ax2.set_title(f"{user} {total_games} games by Map")

    plt.subplots_adjust(wspace=0, hspace=0)

    return fig
