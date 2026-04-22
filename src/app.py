import streamlit as st
import json
import os
from typing import List, Dict, Tuple, Optional

from state import ConversationState
from nl_parser import parse_preferences
from genre_similarity import get_genre_similarity, find_similar_genres
from recommender import load_songs, recommend_songs, score_song


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", ".vibefinder_state.json")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def save_state(state: ConversationState):
    state_dict = state.to_dict()
    with open(CONFIG_PATH, "w") as f:
        json.dump(state_dict, f)


def load_saved_state() -> Optional[Dict]:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def check_edge_cases(profile: Dict, available_genres: List[str], energy_range: Tuple[float, float]) -> List[str]:
    warnings = []
    
    genre = profile.get("genre")
    if genre and genre not in available_genres:
        similar = find_similar_genres(genre, threshold=0.3)
        if similar:
            similar_names = ", ".join([s[0] for s in similar[:3]])
            warnings.append(f"No exact matches for '{genre}' — showing similar genres: {similar_names}")
        else:
            warnings.append(f"No exact matches for '{genre}' — showing closest alternatives")
    
    energy = profile.get("energy")
    if energy:
        min_e, max_e = energy_range
        if energy > max_e + 0.15:
            warnings.append(f"Energy target {energy:.0%} is higher than any song in catalog — adjusting to {max_e:.0%}")
        elif energy < min_e - 0.15:
            warnings.append(f"Energy target {energy:.0%} is lower than any song in catalog — adjusting to {min_e:.0%}")
    
    if profile.get("mood") == "chill" and profile.get("energy", 0) > 0.7:
        warnings.append("Note: High energy + chill mood may conflict — results may vary")
    
    return warnings


def get_confidence_color(score: float) -> str:
    if score >= 0.7:
        return "green"
    elif score >= 0.4:
        return "orange"
    else:
        return "red"


def get_confidence_label(score: float) -> str:
    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Medium"
    else:
        return "Low"


def main():
    st.set_page_config(
        page_title="VibeFinder 2.0",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if "songs" not in st.session_state:
        songs = load_songs(DATA_PATH)
        available_genres = list(set(s["genre"] for s in songs))
        available_moods = list(set(s["mood"] for s in songs))
        energy_values = [s["energy"] for s in songs]
        
        st.session_state.songs = songs
        st.session_state.available_genres = available_genres
        st.session_state.available_moods = available_moods
        st.session_state.energy_range = (min(energy_values), max(energy_values))
    
    saved = load_saved_state()
    if saved and "conversation" not in st.session_state:
        st.session_state.conversation = ConversationState.from_dict(
            saved,
            st.session_state.available_genres,
            st.session_state.energy_range,
            st.session_state.available_moods
        )
    elif "conversation" not in st.session_state:
        st.session_state.conversation = ConversationState(
            available_genres=st.session_state.available_genres,
            catalog_energy_range=st.session_state.energy_range,
            catalog_moods=st.session_state.available_moods
        )
    
    conversation = st.session_state.conversation
    
    with st.sidebar:
        st.header("🎛️ Manual Controls")
        use_manual = st.toggle("Override conversation", value=False)
        
        manual_prefs = {}
        if use_manual:
            st.subheader("Genre")
            manual_genre = st.selectbox(
                "Genre",
                [""] + sorted(st.session_state.available_genres),
                index=0
            )
            if manual_genre:
                manual_prefs["genre"] = manual_genre
            
            st.subheader("Mood")
            mood_options = ["", "happy", "chill", "intense", "moody", "focused", "peaceful", "romantic", "relaxed"]
            manual_mood = st.selectbox("Mood", mood_options, index=mood_options.index("") if "" in mood_options else 0)
            if manual_mood:
                manual_prefs["mood"] = manual_mood
            
            st.subheader("Energy & Mood")
            manual_energy = st.slider("Energy", 0.0, 1.0, 0.5, step=0.05)
            manual_valence = st.slider("Valence (Mood)", 0.0, 1.0, 0.5, step=0.05)
            manual_acousticness = st.slider("Acousticness", 0.0, 1.0, 0.5, step=0.05)
            
            manual_prefs["energy"] = manual_energy
            manual_prefs["valence"] = manual_valence
            manual_prefs["acousticness"] = manual_acousticness
        
        st.divider()
        
        if st.button("🔄 Start Fresh"):
            conversation.reset()
            save_state(conversation)
            st.rerun()
        
        st.caption(f"Confidence: {get_confidence_label(conversation.preference_confidence)} ({conversation.preference_confidence:.0%})")
    
    st.title("🎧 VibeFinder 2.0")
    st.caption("Conversational Music Recommender")
    
    st.subheader("💡 Quick Starts")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("☀️ Morning Run"):
        if "quick_start" not in st.session_state:
            st.session_state.quick_start = "morning_run"
    if col2.button("🌙 Late Night Coding"):
        if "quick_start" not in st.session_state:
            st.session_state.quick_start = "night_coding"
    if col3.button("🏋️ Gym Session"):
        if "quick_start" not in st.session_state:
            st.session_state.quick_start = "gym"
    
    if st.session_state.get("quick_start"):
        quick_input_map = {
            "morning_run": "I want something upbeat for my morning run",
            "night_coding": "Chill music for late night coding",
            "gym": "Something dark and intense for the gym"
        }
        response_map = {
            "morning_run": "Got it! Finding upbeat tracks with high energy for your run.",
            "night_coding": "Perfect! Finding chill lofi tracks to help you focus.",
            "gym": "Finding intense tracks to power your workout!"
        }
        quick_input = quick_input_map[st.session_state.quick_start]
        response = response_map[st.session_state.quick_start]
        
        conversation.user_message_history.append({"role": "user", "content": quick_input})
        parsed = parse_preferences(quick_input)
        conversation.update_profile(parsed)
        conversation.user_message_history.append({"role": "assistant", "content": response})
        save_state(conversation)
        
        del st.session_state["quick_start"]
        st.rerun()
    
    st.divider()
    
    for msg in conversation.user_message_history:
        with st.chat_message(msg["role"], avatar="🎧" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
    
    user_input = st.chat_input("Describe your vibe...")
    
    if user_input:
        conversation.user_message_history.append({"role": "user", "content": user_input})
        
        parsed = parse_preferences(user_input)
        conversation.update_profile(parsed)
        
        clarification = conversation.get_clarification_question()
        
        if clarification:
            response = clarification
            conversation.clarification_needed = clarification
        else:
            if conversation.has_minimum_preferences():
                prefs = conversation.get_active_preferences()
                response = f"Got it! Here's what I found for {prefs.get('genre', 'various') or 'various'} / {prefs.get('mood', 'various') or 'various'} music."
            else:
                response = "Tell me more about what you're in the mood for!"
        
        conversation.user_message_history.append({"role": "assistant", "content": response})
        save_state(conversation)
        st.rerun()
    
    st.divider()
    
    profile_to_use = manual_prefs if use_manual else conversation.get_active_preferences()
    
    if profile_to_use and (st.button("🎵 Get Recommendations", type="primary") or st.session_state.get("show_recommendations", False)):
        st.session_state.show_recommendations = True
        
        st.subheader("📊 Your Profile")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            genre_val = profile_to_use.get("genre", "Any")
            st.metric("Genre", genre_val if genre_val else "Any")
        with col2:
            mood_val = profile_to_use.get("mood", "Any")
            st.metric("Mood", mood_val if mood_val else "Any")
        with col3:
            energy_val = profile_to_use.get("energy")
            st.metric("Energy", f"{energy_val:.0%}" if energy_val else "Any")
        
        conf_score = conversation.preference_confidence
        conf_color = get_confidence_color(conf_score)
        st.progress(conf_score, text=f"Confidence: {get_confidence_label(conf_score)} ({conf_score:.0%})")
        
        warnings = check_edge_cases(
            profile_to_use,
            st.session_state.available_genres,
            st.session_state.energy_range
        )
        
        for warning in warnings:
            st.warning(warning)
        
        st.subheader("🎵 Recommendations")
        
        recommendations = recommend_songs(profile_to_use, st.session_state.songs, k=5)
        
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            with st.expander(f"#{rank} {song['title']} — {song['artist']}", expanded=(rank==1)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Genre:** {song['genre']}  |  **Mood:** {song['mood']}")
                    st.markdown(f"Energy: {song['energy']:.0%}  |  Valence: {song['valence']:.0%}  |  Acousticness: {song['acousticness']:.0%}")
                with col2:
                    st.markdown(f"### {score:.0%}")
                
                with st.expander("Why this?", expanded=False):
                    st.caption(explanation)
                    
                    if profile_to_use.get("genre"):
                        sim = get_genre_similarity(song['genre'], profile_to_use['genre'])
                        if sim < 1.0 and sim > 0.0:
                            st.caption(f"Genre proximity: {sim:.0%} similar to your preference")


if __name__ == "__main__":
    main()