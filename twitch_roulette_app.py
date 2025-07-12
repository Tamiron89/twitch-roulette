import streamlit as st
import requests
import random

# Deine Zugangsdaten
CLIENT_ID = 'ojb9ukjr8tq0p8d91ytqis7k94vduf'
ACCESS_TOKEN = 'pnp1208zpgbsujpv9nz5fnbi4747b7'

HEADERS = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# Twitch Game-ID holen
def get_game_id(game_name):
    url = 'https://api.twitch.tv/helix/games'
    params = {'name': game_name}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    if data['data']:
        return data['data'][0]['id']
    return None

# Bis zu 800 Streams holen
def get_streams(max_viewers, game_id=None, max_pages=8):
    all_streams = []
    cursor = None

    for _ in range(max_pages):
        params = {'language': 'de', 'first': 100}
        if game_id:
            params['game_id'] = game_id
        if cursor:
            params['after'] = cursor

        response = requests.get('https://api.twitch.tv/helix/streams', headers=HEADERS, params=params)
        data = response.json()

        if 'data' not in data:
            break

        filtered = [s for s in data['data'] if s['viewer_count'] < max_viewers]
        all_streams.extend(filtered)

        cursor = data.get('pagination', {}).get('cursor')
        if not cursor:
            break

    return all_streams

# Stream anzeigen
def show_random_stream(streams):
    if not streams:
        st.warning("Keine passenden Streams gefunden.")
        return

    chosen = random.choice(streams)
    st.success("🎲 Dein Twitch Roulette Ergebnis:")
    st.markdown(f"**👤 Streamer:** [{chosen['user_name']}](https://twitch.tv/{chosen['user_name']})")
    st.markdown(f"**🎮 Spiel:** {chosen['game_name']}")
    st.markdown(f"**👀 Zuschauer:** {chosen['viewer_count']}")

# UI starten
st.set_page_config(page_title="Twitch Roulette", layout="centered")
st.title("🎲 Tamiron's Twitch Roulette")
st.write("Finde zufällig kleine deutschsprachige Streamer auf Twitch!")

max_viewers = st.number_input("🔢 Max. Zuschauer", min_value=1, value=20, step=1)
category = st.text_input("🎮 Kategorie (optional)", placeholder="Just Chatting, Minecraft...")

if st.button("🎲 Stream ziehen"):
    game_id = get_game_id(category) if category else None
    with st.spinner("Suche läuft..."):
        streams = get_streams(max_viewers, game_id)
        show_random_stream(streams)
