# Steamlit app for Beyond All Reason

from enum import auto, StrEnum

from urllib.parse import quote
from urllib.request import urlopen
import matplotlib.pyplot as plt

import streamlit as st

from bai import plot_win_rate

plt.rcParams["figure.figsize"] = (10, 10)


class Preset(StrEnum):
    """Preset for the API call"""

    duel = auto()
    team = auto()
    ffa = auto()
    all = auto()


if __name__ == "__main__":
    st.image(
        "https://assets.website-files.com/5c68622246b367adf6f3041d/604dcda159681e01ba36b19b_BAR%20LOGO%20WEB%20(1).svg",
        width=100,
    )
    st.title("Beyond All Information")
    instructions = """
        Get your stats of Beyond All Reason https://www.beyondallreason.info
        """
    st.write(instructions)

    preset = Preset(st.sidebar.selectbox("Game Preset", ["team", "duel", "ffa", "all"]))
    user: str = st.sidebar.text_input("Player name", "furyhawk")
    min_games: int = st.sidebar.slider(
        "Min Games", min_value=1, max_value=20, value=5, step=1
    )
    season0: bool = st.sidebar.checkbox("Season 0", value=False)

    progress_text = "Operation in progress. Please wait."
    matches_bar = st.progress(0, text=progress_text)
    figure = plot_win_rate(matches_bar, user, min_games, season0, preset)
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
