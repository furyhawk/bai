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
def controller(
    matches_bar,
    user: str,
    min_games: int = 5,
    preset=Preset.team,
    season0: bool = False,
):
    df = process_match_data(get_match_data(matches_bar, user, preset, season0))
    win_rate_df = get_win_rate(df, user, min_games)
    if win_rate_df.empty:
        st.write(f"No data for {user} with {min_games} games")
        return

    fig = plot_win_rate(win_rate_df, user, preset)
    if fig:
        st.pyplot(fig)
    col_best, col_worst, col_fraction = st.columns(3)

    top_n = 10
    best_teammates_df = get_best_teammates(df, user, min_games)
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
        fractions_win_rate_df = get_fractions_win_rate(df, user)
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


def main():
    # Initialize session state
    if "user" not in st.session_state:
        st.session_state.user = "furyhawk"

    st.set_page_config(
        page_title="Beyond All Information",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header
    st.image(
        "https://assets.website-files.com/5c68622246b367adf6f3041d/604dcda159681e01ba36b19b_BAR%20LOGO%20WEB%20(1).svg",
        width=100,
    )
    st.title("Beyond All Information")
    instructions = """
        Get your stats of Beyond All Reason https://www.beyondallreason.info
        """
    st.write(instructions)

    # Sidebar
    preset = Preset(st.sidebar.selectbox("Game Preset", ["team", "duel", "ffa", "all"]))
    st.sidebar.text_input("Player name", key="user")
    min_games: int = st.sidebar.slider(
        "Min Games", min_value=1, max_value=20, value=3, step=1
    )
    season0: bool = st.sidebar.checkbox("Season 0", True)

    # Main
    tab_battle, tab_user = st.tabs(["Battle", "User Stats"])
    with tab_user:
        if st.session_state.user:
            progress_text = "Operation in progress. Please wait."
            matches_bar = st.progress(0, text=progress_text)
            controller(matches_bar, st.session_state.user, min_games, preset, season0)

    with tab_battle:
        with st.spinner("Wait for it..."):
            battles_df = get_battle_list()
            battle_detail_df = get_battle_details(battles_df)
            team_size = len(battle_detail_df.index)
            # st.dataframe(battle_detail_df.head(team_size // 2))
            # st.dataframe(battle_detail_df.tail(team_size // 2))

            battle_list = []

            for _, player in battle_detail_df.iterrows():
                battle = {}
                win_rate_df = get_quick_match_data(player["username"], preset)
                win_rate_user_df = get_quick_win_rate(win_rate_df, min_games)
                map_df = get_map_win_rate(win_rate_user_df, player["map"])
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

            battle_win_rate_df = pd.DataFrame(battle_list)
            team1_df = battle_win_rate_df.head(team_size // 2)
            team2_df = battle_win_rate_df.tail(team_size // 2)
            team1_avg_win_rate = team1_df.agg({"mean": ["mean", "count"]})["mean"][0]
            team1_total_skills = team1_df["skill"].sum()
            team1_total_games = team1_df["count"].sum()
            team2_avg_win_rate = team2_df.agg({"mean": ["mean", "count"]})["mean"][0]
            team2_total_skills = team2_df["skill"].sum()
            team2_total_games = team2_df["count"].sum()

            st.dataframe(team1_df)
            col1_win_rate, col1_skill, col1_games = st.columns(3)
            col1_win_rate.metric(
                "Team 1 win rate",
                f"{team1_avg_win_rate:.0%}",
                f"{team1_avg_win_rate-team2_avg_win_rate:.0%}",
            )
            col1_skill.metric("Team 1 total skills", f"{team1_total_skills:.0f}")
            col1_games.metric("Team 1 total games", f"{team1_total_games:.0f}")

            st.dataframe(team2_df)
            col2_win_rate, col2_skill, col2_games = st.columns(3)
            col2_win_rate.metric(
                "Team 2 win rate",
                f"{team2_avg_win_rate:.0%}",
                f"{team2_avg_win_rate-team1_avg_win_rate:.0%}",
            )
            col2_skill.metric("Team 2 total skills", f"{team2_total_skills:.0f}")
            col2_games.metric("Team 2 total games", f"{team2_total_games:.0f}")


if __name__ == "__main__":
    main()
