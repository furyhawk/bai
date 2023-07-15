# Steamlit app for Beyond All Reason

from enum import auto, StrEnum

import matplotlib.pyplot as plt
import pandas as pd

import streamlit as st

from bai.bai import (
    get_quick_match_data,
    get_quick_win_rate,
    get_win_rate,
    get_fractions_win_rate,
    get_best_teammates,
    get_match_data,
    process_match_data,
    plot_win_rate,
    get_battle_list,
    get_battle_details,
    get_map_win_rate,
)

plt.rcParams["figure.figsize"] = (10, 10)


class Preset(StrEnum):
    """Preset for the API call"""

    duel = auto()
    team = auto()
    ffa = auto()
    all = auto()


# Controller for the streamlit app
def player_tab_controller(
    matches_bar,
    player: str,
    min_games: int = 5,
    preset=Preset.team,
    season0: bool = False,
):
    df = process_match_data(get_match_data(matches_bar, player, preset, season0))
    win_rate_df = get_win_rate(df, player, min_games)
    if win_rate_df.empty:
        st.write(f"No data for {player} with {min_games} games")
        return

    fig = plot_win_rate(win_rate_df, player, preset)
    if fig:
        st.pyplot(fig)
    col_best, col_worst, col_fraction = st.columns(3)

    top_n = 10
    best_teammates_df = get_best_teammates(df, player, min_games)
    with col_best:
        if not best_teammates_df.empty:
            st.dataframe(
                best_teammates_df.head(top_n),
                column_config={
                    "name": "Best Teammates",
                    "userId": None,
                    "mean": st.column_config.NumberColumn(
                        "Win rate",
                        help="Win rate of the player with Best Teammates",
                        format="%.2f",
                    ),
                    "count": st.column_config.NumberColumn(
                        "Games",
                        help="Number of games played with Best Teammates",
                        format="%d 🎮",
                    ),
                },
            )

    with col_worst:
        if not best_teammates_df.empty:
            st.dataframe(
                best_teammates_df.sort_values(
                    [("mean"), ("count")], ascending=True
                ).head(top_n),
                column_config={
                    "name": "Lobster with",
                    "userId": None,
                    "mean": st.column_config.NumberColumn(
                        "Win rate",
                        help="Win rate of the player with Lobsters",
                        format="%.2f",
                    ),
                    "count": st.column_config.NumberColumn(
                        "Games",
                        help="Number of games played with Lobsters",
                        format="%d 🎮",
                    ),
                },
            )

    with col_fraction:
        fractions_win_rate_df = get_fractions_win_rate(df, player)
        if not fractions_win_rate_df.empty:
            st.dataframe(
                fractions_win_rate_df,
                column_config={
                    "faction": "Factions Win Rate",
                    "mean": st.column_config.NumberColumn(
                        "Win rate",
                        help="Win rate of the player with faction",
                        format="%.2f",
                    ),
                    "count": st.column_config.NumberColumn(
                        "Games",
                        help="Number of games played with faction",
                        format="%d 🎮",
                    ),
                },
            )

def on_change_player():
    st.experimental_set_query_params(
        player=str(st.session_state.player),
    )


def main():
    # Initialize session state

    params = st.experimental_get_query_params()
    print(params)
    if "player" in params:
        st.session_state.player = params["player"][0]

    if "player" not in st.session_state:
        st.session_state.player = "furyhawk"

    st.experimental_set_query_params(
        player=str(st.session_state.player),
    )


    st.set_page_config(
        page_title="Beyond All Information",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


    # Header
    image_col, title_col = st.columns([1, 5], gap="small")
    with image_col:
        st.image(
            "https://assets.website-files.com/5c68622246b367adf6f3041d/604dcda159681e01ba36b19b_BAR%20LOGO%20WEB%20(1).svg",
            # width=100,
        )
    with title_col:
        st.title("Beyond All Information")

    instructions = """
        Get your stats of Beyond All Reason https://www.beyondallreason.info
            """
    st.caption(instructions)

    # Sidebar
    preset = Preset(st.sidebar.selectbox("Game Preset", ["team", "duel", "ffa", "all"]))
    st.sidebar.text_input("Player name", key="player", on_change=on_change_player)
    min_games: int = st.sidebar.slider(
        "Min Games", min_value=1, max_value=20, value=3, step=1
    )
    season0: bool = st.sidebar.checkbox("Season 0", True)

    # Main
    tab_battle, tab_player = st.tabs(["Battle", "Player Stats"])
    with tab_player:
        st.caption("Get the win rate of player by map")
        if st.session_state.player:
            progress_text = "Operation in progress. Please wait."
            matches_bar = st.progress(0, text=progress_text)
            player_tab_controller(
                matches_bar, st.session_state.player, min_games, preset, season0
            )
            matches_bar.empty()

    with tab_battle:
        st.caption("Get the win rate of players in the battle with most spectators")
        battles_df = get_battle_list()
        battle_detail_df = get_battle_details(battles_df)

        progress_text = "Operation in progress. Please wait."
        battle_bar = st.progress(0, text=progress_text)

        initial_battle_placeholder = st.empty()
        initial_battle_placeholder.dataframe(battle_detail_df)

        number_of_players = len(battle_detail_df.index)
        percent_complete = 0
        battle_list = []

        for _, player in battle_detail_df.iterrows():
            percent_complete += 1
            battle_bar.progress(
                percent_complete / number_of_players,
                text=f"Getting API for player {percent_complete} out of {number_of_players} players. ({player['username']})",
            )
            battle = {}

            win_rate_df = get_quick_match_data(player["username"], preset)
            win_rate_player_df = get_quick_win_rate(win_rate_df, 1)
            map_df = get_map_win_rate(win_rate_player_df, player["map"])
            if not map_df.empty:
                record = map_df.to_dict("records")[-1]
                battle = {
                    "teamId": player["teamId"],
                    "userId": player["userId"],
                    "username": player["username"],
                    "skill": player["skill"],
                    "gameStatus": player["gameStatus"],
                    **record,
                }
            else:
                battle = {
                    "teamId": player["teamId"],
                    "userId": player["userId"],
                    "username": player["username"],
                    "skill": player["skill"],
                    "gameStatus": player["gameStatus"],
                    "Map.fileName": player["map"],
                    "mean": 0.5,
                    "count": 0,
                }
            battle_list.append(battle)

        battle_bar.empty()
        initial_battle_placeholder.empty()

        battle_win_rate_df = pd.DataFrame(battle_list)
        team1_df = battle_win_rate_df.head(number_of_players // 2)
        team2_df = battle_win_rate_df.tail(number_of_players // 2)

        team1_avg_win_rate = team1_df.agg({"mean": ["mean", "count"]})["mean"][0]
        team1_total_skills = team1_df["skill"].sum()
        team1_total_games = team1_df["count"].sum()

        team2_avg_win_rate = team2_df.agg({"mean": ["mean", "count"]})["mean"][0]
        team2_total_skills = team2_df["skill"].sum()
        team2_total_games = team2_df["count"].sum()

        # Battle
        map_name = team1_df["Map.fileName"].iloc[0]  # lobby 0
        image_col, title_col = st.columns([1, 5], gap="small")
        with image_col:
            st.image(f"https://api.bar-rts.com/maps/{map_name}/texture-mq.jpg")
        with title_col:
            st.subheader(f"Map: {map_name}")

        # Team 1
        team1_container = st.container()
        team1_container.dataframe(
            team1_df,
            column_config={
                "teamId": None,
                "userId": None,
                "Map.fileName": None,
                "mean": st.column_config.NumberColumn(
                    "win rate",
                    help="Win rate on this map",
                    format="%.2f",
                ),
                "count": st.column_config.NumberColumn(
                    "games",
                    help="Number of games played on this map",
                    format="%d 🎮",
                ),
            },
            hide_index=True,
        )

        col1_win_rate, col1_skill, col1_games = team1_container.columns(3)
        col1_win_rate.metric(
            "Team 1 win rate",
            f"{team1_avg_win_rate:.0%}",
            f"{team1_avg_win_rate-team2_avg_win_rate:.0%}",
        )
        col1_skill.metric("Team 1 total skills", f"{team1_total_skills:.0f}")
        col1_games.metric("Team 1 total games", f"{team1_total_games:.0f}")

        # Team 2
        team2_container = st.container()
        col2_win_rate, col2_skill, col2_games = team2_container.columns(3)
        col2_win_rate.metric(
            "Team 2 win rate",
            f"{team2_avg_win_rate:.0%}",
            f"{team2_avg_win_rate-team1_avg_win_rate:.0%}",
        )
        col2_skill.metric("Team 2 total skills", f"{team2_total_skills:.0f}")
        col2_games.metric("Team 2 total games", f"{team2_total_games:.0f}")

        team2_container.dataframe(
            team2_df,
            column_config={
                "teamId": None,
                "userId": None,
                "Map.fileName": None,
                "mean": st.column_config.NumberColumn(
                    "win rate",
                    help="Win rate on this map",
                    format="%.2f",
                ),
                "count": st.column_config.NumberColumn(
                    "games",
                    help="Number of games played on this map",
                    format="%d 🎮",
                ),
            },
            hide_index=True,
        )


if __name__ == "__main__":
    main()
