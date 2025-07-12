import streamlit as st
import requests
import random

# === 🔐 Deine Zugangsdaten ===
CLIENT_ID = 'ojb9ukjr8tq0p8d91ytqis7k94vduf'
ACCESS_TOKEN = 'pnp1208zpgbsujpv9nz5fnbi4747b7'

HEADERS = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# === 🎯 Twitch Game-ID holen ===
def get_game_id(game_name):
    url = 'https://api.twitch.tv/helix/games'
    params = {'name': game_name}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    if data['data']:
        return data['data'][0]['id']
    return None

# === 🔄 Streams holen ===
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

# === 🎥 Stream anzeigen ===
def show_random_stream(streams):
    if not streams:
        st.warning("Keine passenden Streams gefunden.")
        return

    chosen = random.choice(streams)
    st.success("🎲 Dein Twitch Roulette Ergebnis:")
    st.markdown(f"**👤 Streamer:** [{chosen['user_name']}](https://twitch.tv/{chosen['user_name']})")
    st.markdown(f"**🎮 Spiel:** {chosen['game_name']}")
    st.markdown(f"**👀 Zuschauer:** {chosen['viewer_count']}")

# === UI ===
st.set_page_config(page_title="Twitch Roulette", layout="centered")
st.title("🎲 Tamiron's Twitch Roulette")
st.caption("Zufällig kleine deutschsprachige Streamer entdecken!")

max_viewers = st.number_input("🔢 Max. Zuschauer", min_value=1, value=20, step=1)

# ========== SESSION HANDLING ==========
if "chosen_game" not in st.session_state:
    st.session_state["chosen_game"] = None

if "category_query" not in st.session_state:
    st.session_state["category_query"] = ""

# === Kategorie zurücksetzen ===
if st.session_state["chosen_game"]:
    st.markdown(f"✅ **Gewählte Kategorie:** *{st.session_state['chosen_game']['name']}*")
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("🎲 Stream ziehen"):
            with st.spinner("Würfle..."):
                streams = get_streams(max_viewers, st.session_state["chosen_game"]["id"])
                show_random_stream(streams)
    with colB:
        if st.button("🔁 Kategorie zurücksetzen"):
            st.session_state["chosen_game"] = None
            st.session_state["category_query"] = ""

else:
    # === Kategorie suchen + Auswahl
    st.subheader("🎮 Kategorie suchen")
    category_query = st.text_input("Suchbegriff eingeben:", value=st.session_state["category_query"])
    st.session_state["category_query"] = category_query

    if category_query:
        url = 'https://api.twitch.tv/helix/search/categories'
        params = {'query': category_query}
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()

        if data.get("data"):
            top_matches = data["data"][:6]  # Max. 6 Kategorien anzeigen
            for item in top_matches:
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(item["box_art_url"].replace("{width}", "100").replace("{height}", "140"))
                with col2:
                    st.markdown(f"**{item['name']}**")
                    if st.button(f"✅ Wählen: {item['name']}", key=item['id']):
                        st.session_state["chosen_game"] = {
                            "id": item["id"],
                            "name": item["name"]
                        }
                        st.success(f"✅ Kategorie gesetzt: {item['name']}")
        else:
            st.info("Keine passenden Kategorien gefunden.")
    else:
        st.caption("🔍 Gib z. B. 'chat' oder 'mine' ein, um Kategorien zu finden.")

# === Fallback: Suche ohne Kategorie ===
if not st.session_state["chosen_game"]:
    if st.button("🎲 Stream ziehen (alle Kategorien)"):
        with st.spinner("Würfle..."):
            streams = get_streams(max_viewers)
            show_random_stream(streams)
