# Steamlit app for Beyond All Reason

from enum import auto, StrEnum

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import streamlit as st

from bai import (
    get_win_rate,
    get_fractions_win_rate,
    get_best_teammates,
    get_match_data,
    process_match_data,
    get_battle_list,
    get_battle_details,
)

plt.rcParams["figure.figsize"] = (10, 10)


class Preset(StrEnum):
    """Preset for the API call"""

    duel = auto()
    team = auto()
    ffa = auto()
    all = auto()


# Set the x axis minor locator to 5 and major locator to 10
# Set the y axis to the map name
def plot_win_rate(
    win_rate,
    user: str,
    preset=Preset.team,
):
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
    tab_user, tab_battle = st.tabs(["User Stats", "Battle"])
    with tab_user:
        if st.session_state.user:
            progress_text = "Operation in progress. Please wait."
            matches_bar = st.progress(0, text=progress_text)
            controller(matches_bar, st.session_state.user, min_games, preset, season0)

    with tab_battle:
        battles_df = get_battle_list()
        battle_detail_df = get_battle_details(battles_df)
        team_size = len(battle_detail_df.index)
        st.dataframe(battle_detail_df.head(team_size // 2))
        st.dataframe(battle_detail_df.tail(team_size // 2))


if __name__ == "__main__":
    main()
