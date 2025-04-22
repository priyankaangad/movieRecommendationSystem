import streamlit as st
import streamlit_option_menu
from streamlit_extras.stoggle import stoggle
from processing import preprocess
from processing.display import Main

# Setting the wide mode as default
st.set_page_config(layout="wide")

displayed = []

# Initialize session state
st.session_state.setdefault('movie_number', 0)
st.session_state.setdefault('selected_movie_name', "")
st.session_state.setdefault('user_menu', "")


def main():
    def initial_options():
        # Vertical menu in the sidebar
        with st.sidebar:
            st.markdown("## 🎬 Movie Recommender")
            st.session_state.user_menu = streamlit_option_menu.option_menu(
                menu_title=None,  # no header since we have our own markdown
                options=[
                    "Recommend me a similar movie",
                    "Describe me a movie",
                    "Check all Movies",
                ],
                icons=["film", "info-circle", "grid-3x3"],
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
            )

        # Dispatch to the right view
        if st.session_state.user_menu == "Recommend me a similar movie":
            recommend_display()
        elif st.session_state.user_menu == "Describe me a movie":
            display_movie_details()
        else:  # "Check all Movies"
            paging_movies()

    def recommend_display():
        st.title("Movie Recommender System")
        selected_movie_name = st.selectbox(
            "Select a Movie...", new_df["title"].values
        )
        if st.button("Recommend"):
            st.session_state.selected_movie_name = selected_movie_name
            recommendation_tags(new_df, selected_movie_name,
                                r"Files/similarity_tags_tags.pkl", "are")
            recommendation_tags(new_df, selected_movie_name,
                                r"Files/similarity_tags_genres.pkl", "on the basis of genres are")
            recommendation_tags(new_df, selected_movie_name,
                                r"Files/similarity_tags_prduction_comp.pkl", "from the same production company are")
            recommendation_tags(new_df, selected_movie_name,
                                r"Files/similarity_tags_keywords.pkl", "on the basis of keywords are")
            recommendation_tags(new_df, selected_movie_name,
                                r"Files/similarity_tags_tcast.pkl", "on the basis of cast are")

    def recommendation_tags(df, movie_name, pickle_path, desc):
        movies, posters = preprocess.recommend(df, movie_name, pickle_path)
        st.subheader(f"Best recommendations {desc}...")
        rec_movies, rec_posters = [], []
        for m, p in zip(movies, posters):
            if len(rec_movies) == 5:
                break
            if m not in displayed:
                rec_movies.append(m)
                rec_posters.append(p)
                displayed.append(m)

        cols = st.columns(5)
        for col, title, poster in zip(cols, rec_movies, rec_posters):
            with col:
                st.text(title)
                st.image(poster)

    def display_movie_details():
        st.title("Movie Details")

        # Let the user choose which movie to describe
        movie_name = st.selectbox(
            "Select a movie to describe:",
            new_df["title"].values,
            index=0,
            key="describe_selectbox"
        )
        # Persist selection
        st.session_state.selected_movie_name = movie_name

        # Now safe to fetch details
        info = preprocess.get_details(movie_name)

        with st.container():
            image_col, text_col = st.columns((1, 2))
            with image_col:
                st.image(info[0])

            with text_col:
                st.title(movie_name)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rating", info[8])
                with col2:
                    st.metric("No. of ratings", info[9])
                with col3:
                    st.metric("Runtime", f"{info[6]} min")

                st.markdown("**Overview**")
                st.write(info[3])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Release Date:** {info[4]}")
                with col2:
                    st.markdown(f"**Budget:** ${info[1]:,}")
                with col3:
                    st.markdown(f"**Revenue:** ${info[5]:,}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Genres:** " + " · ".join(info[2]))
                with col2:
                    st.markdown("**Available in:** " + " · ".join(info[13]))
                with col3:
                    st.markdown("**Directed by:** " + info[12][0])

        st.header("Cast")
        urls, bios = [], []
        for pid in info[14][:5]:
            url, bio = preprocess.fetch_person_details(pid)
            urls.append(url)
            bios.append(bio)

        cols = st.columns(5)
        for col, u, b in zip(cols, urls, bios):
            with col:
                st.image(u)
                stoggle("Show More", b)

    def paging_movies():
        max_pages = len(movies) // 10
        col_prev, col_slider, col_next = st.columns([1, 9, 1])

        with col_prev:
            if st.button("Prev") and st.session_state.movie_number >= 10:
                st.session_state.movie_number -= 10

        with col_slider:
            pg = st.slider("Page", 0, max_pages, st.session_state.movie_number // 10)
            st.session_state.movie_number = pg * 10

        with col_next:
            if st.button("Next") and st.session_state.movie_number + 10 < len(movies):
                st.session_state.movie_number += 10

        display_all_movies(st.session_state.movie_number)

    def display_all_movies(start):
        i = start
        for _ in range(2):  # two rows
            cols = st.columns(5)
            for col in cols:
                m_id = movies.iloc[i]["movie_id"]
                poster = preprocess.fetch_posters(m_id)
                col.image(poster, caption=movies.iloc[i]["title"])
                i += 1

    # Load data & show menu
    with Main() as bot:
        bot.main_()
        new_df, movies, movies2 = bot.getter()
    initial_options()


if __name__ == "__main__":
    main()
