# Steamlit app for Beyond All Reason

from enum import auto, StrEnum

from urllib.parse import quote
from urllib.request import urlopen
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import streamlit as st

plt.rcParams["figure.figsize"] = (10, 10)


class Preset(StrEnum):
    """Preset for the API call"""

    duel = auto()
    team = auto()
    ffa = auto()
    all = auto()


preset = Preset.team


@st.cache_data
def get_data(url: str):
    """Get the data from the API and return a json object"""
    with urlopen(url) as response:
        source = response.read().decode("utf-8")
    data = json.loads(source)
    return data


# Get the players replays metadata
def get_match_data(user: str, preset: Preset = Preset.all):
    # Depending on the preset, the API returns different data.json
    # The preset uses the following format: &preset=duel%2Cffa%2Cteam
    # duel%2Cffa%2Cteam is the same as duel,ffa,team

    if preset == Preset.all:
        preset = "&preset=duel&preset=ffa&preset=team"
    else:
        preset = f"&preset={preset.name}"

    uri = f"https://api.bar-rts.com/replays?page=1&limit=999{preset}&hasBots=false&endedNormally=true&players="

    data = get_data(f"{uri}{quote(user)}")

    # Get the winning team and count the number of wins
    match = {}
    matches = []

    for game in data["data"]:
        if game["Map"]["fileName"] is not None:
            for team in game["AllyTeams"]:
                for player in team["Players"]:
                    if player["name"] == user:
                        match = {
                            **match,
                            **{
                                "id": game["id"],
                                "name": player["name"],
                                "winningTeam": team["winningTeam"],
                                "Map.fileName": game["Map"]["fileName"]
                                + "_"
                                + str(len(team["Players"]))
                                + "v"
                                + str(len(team["Players"])),
                                "Map.scriptName": game["Map"]["scriptName"],
                                "durationMs": game["durationMs"],
                                "startTime": game["startTime"],
                            },
                        }
                        matches.append(match)

    matches_df = pd.json_normalize(matches)
    matches_df["startTime"] = pd.to_datetime(matches_df["startTime"])
    return matches_df


# Get the win rate for each map
def get_win_rate(user: str, min_games: int = 5, season0: bool = False):
    df = get_match_data(user, preset)
    if df.empty:
        return df

    if season0:
        df = df[df["startTime"] >= "2023-06-01"]

    win_rate = (
        df.groupby(["Map.fileName"])
        .agg({"winningTeam": ["mean", "count"]})["winningTeam"]
        .query(f"count >= {str(min_games)}")
        .sort_values([("mean"), ("count")], ascending=True)
    )
    return win_rate


# Use win_rate and plot the winning % for each map with the number of
# games played with horizontal bars and subdivide the bars by the winning team
# with minor locator for the x axis. Color by count and winningTeam.


# Set the x axis minor locator to 5 and major locator to 10
# Set the y axis to the map name
def plot_win_rate(user: str, min_games: int = 5, season0: bool = False):
    win_rate = get_win_rate(user, min_games, season0)
    if win_rate.empty:
        print(f"{user} has not played enough games")
        return

    # Get overall win rate
    overall_win_rate = win_rate["mean"].mean()
    # Get total number of games
    total_games = win_rate["count"].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey="all", figsize=(12, 6))

    bars = ax1.barh(
        y=win_rate.index,
        width=win_rate["mean"],
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
    ax1.set_title(f"[{preset.name} games]{user} Winning {overall_win_rate:.0%} by Map")

    ax1.set_axisbelow(True)

    bars = ax2.barh(
        y=win_rate.index,
        width=win_rate["count"],
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


if __name__ == "__main__":
    st.title("Beyond All Information")
    instructions = """
        Get your stats of Beyond All Reason https://www.beyondallreason.info/.
        """
    st.write(instructions)

    preset = Preset(st.sidebar.selectbox("Game Preset", ["team", "duel", "ffa", "all"]))
    user: str = st.sidebar.text_input("Player name", "furyhawk")
    min_games: int = st.sidebar.slider(
        "Min Games", min_value=1, max_value=20, value=5, step=1
    )
    season0: bool = st.sidebar.checkbox("Season 0", value=False)

    figure = plot_win_rate(user, min_games, season0)
    if figure is not None:
        st.pyplot(figure)
    else:
        st.write(f"{user} has not played enough games")

    # st.image(
    #     "https://assets.website-files.com/5c68622246b367adf6f3041d/604dcda159681e01ba36b19b_BAR%20LOGO%20WEB%20(1).svg"
    # )

    # leaderboards = get_data("https://api.bar-rts.com/leaderboards")
    # team_leaderboards_df = pd.json_normalize(leaderboards[preset.name])
    # st.dataframe(team_leaderboards_df)
