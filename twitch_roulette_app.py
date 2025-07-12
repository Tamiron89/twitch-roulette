import streamlit as st
import requests
import random

# === 🔐 Zugangsdaten ===
CLIENT_ID = 'ojb9ukjr8tq0p8d91ytqis7k94vduf'
ACCESS_TOKEN = 'pnp1208zpgbsujpv9nz5fnbi4747b7'

HEADERS = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# === 🎯 Streams holen ===
def get_streams(max_viewers, game_ids=None, max_pages=8):
    all_streams = []
    cursor = None

    for _ in range(max_pages):
        params = {'language': 'de', 'first': 100}
        if game_ids:
            params['game_id'] = game_ids
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

# === 📺 Stream anzeigen ===
def show_random_stream(streams):
    if not streams:
        st.warning("Keine passenden Streams gefunden.")
        return

    chosen = random.choice(streams)
    st.success("🎲 Dein Twitch Roulette Ergebnis:")
    st.image(
        chosen["thumbnail_url"].replace("{width}", "640").replace("{height}", "360"),
        use_container_width=True
    )
    st.markdown(f"**👤 Streamer:** [{chosen['user_name']}](https://twitch.tv/{chosen['user_name']})")
    st.markdown(f"**🎮 Spiel:** {chosen['game_name']}")
    st.markdown(f"**👀 Zuschauer:** {chosen['viewer_count']}")

# === UI Setup ===
st.set_page_config(page_title="Twitch Roulette", layout="centered")
st.title("🎲 Tamiron's Twitch Roulette")
st.caption("Zufällige deutschsprachige Streams entdecken – mit Stil.")

max_viewers = st.number_input("🔢 Max. Zuschauer", min_value=1, value=20, step=1)

# === Session-Setup
if "selected_games" not in st.session_state:
    st.session_state["selected_games"] = []

if "query" not in st.session_state:
    st.session_state["query"] = ""

# === Kategorie-Suche
st.subheader("🎮 Kategorie(n) suchen & auswählen")
query = st.text_input("🔍 Suchbegriff (z. B. 'chat', 'music')", value=st.session_state["query"])
st.session_state["query"] = query

if query:
    url = 'https://api.twitch.tv/helix/search/categories'
    params = {'query': query}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if data.get("data"):
        top_matches = data["data"][:8]  # Max. 8 anzeigen
        for item in top_matches:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(item["box_art_url"].replace("{width}", "100").replace("{height}", "140"))
            with col2:
                st.markdown(f"**{item['name']}**")
                if item["id"] not in [g["id"] for g in st.session_state["selected_games"]]:
                    if st.button(f"✅ Hinzufügen", key=item["id"]):
                        st.session_state["selected_games"].append({
                            "id": item["id"],
                            "name": item["name"]
                        })
                else:
                    st.markdown("✅ Bereits ausgewählt")

# === Auswahl zeigen & zurücksetzen
if st.session_state["selected_games"]:
    st.markdown("### 🧾 Gewählte Kategorien:")
    for g in st.session_state["selected_games"]:
        st.markdown(f"- {g['name']}")

    if st.button("🔁 Auswahl zurücksetzen"):
        st.session_state["selected_games"] = []

# === Stream ziehen
draw = st.button("🎲 Stream ziehen")

if draw:
    selected_ids = [g["id"] for g in st.session_state["selected_games"]]
    with st.spinner("Würfle..."):
        streams = get_streams(max_viewers, selected_ids if selected_ids else None)
        show_random_stream(streams)
