import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- Seiteneinstellungen mit deinem Logo ---
try:
    if os.path.exists("Screenshot_20260908_025914_Google.jpg"):
        logo_image = Image.open("Screenshot_20260908_025914_Google.jpg")
        st.set_page_config(page_title="Team Manager & Card Creator", layout="wide", page_icon=logo_image)
    else:
        st.set_page_config(page_title="Team Manager & Card Creator", layout="wide", page_icon="⚽")
except:
    st.set_page_config(page_title="Team Manager & Card Creator", layout="wide", page_icon="⚽")

# --- Daten-Speicher (Session State) ---
if "players" not in st.session_state:
    st.session_state.players = {}
if "matches" not in st.session_state:
    st.session_state.matches = []

# --- Positionsabhängige Rating-Berechnung ---
def calculate_positional_rating(pos, pac, sho, pas, dri, def_stat, phy):
    if pos in ["ST", "LF", "RF"]:
        return (sho * 0.40) + (pac * 0.30) + (dri * 0.15) + (pas * 0.10) + (phy * 0.05)
    elif pos in ["ZM", "ZOM", "ZDM", "LM", "RM"]:
        return (pas * 0.40) + (dri * 0.30) + (pac * 0.10) + (def_stat * 0.10) + (phy * 0.10)
    elif pos in ["IV", "LV", "RV"]:
        return (def_stat * 0.50) + (phy * 0.30) + (pac * 0.10) + (pas * 0.10)
    elif pos == "TW":
        return (def_stat * 0.50) + (phy * 0.30) + (pas * 0.20)
    else:
        return np.mean([pac, sho, pas, dri, def_stat, phy])

# --- HILFSFUNKTION: ECHTE FUT-KARTE ZEICHNEN ---
def generate_fut_card(name, rating, pos, pac, sho, pas, dri, def_stat, phy, image_file=None):
    # Erzwinge das Laden der card_template.png aus deinem GitHub-Ordner
    try:
        card = Image.open("card_template.png").convert("RGBA")
        card = card.resize((450, 650)) # Perfekt gestreckt für mobile Bildschirme
    except Exception as e:
        # Fallback falls es absolut gar nicht geht
        card = Image.new("RGBA", (450, 650), "#1e0b36")
        draw = ImageDraw.Draw(card)
        draw.rectangle([(10, 10), (440, 640)], outline="#d4af37", width=5)
        
    draw = ImageDraw.Draw(card)
    
    # Spielerbild einfügen falls hochgeladen
    if image_file:
        try:
            p_img = Image.open(image_file).convert("RGBA").resize((180, 200))
            # Positioniert das Gesicht im oberen rechten Bereich der Neymar-Karte
            card.paste(p_img, (190, 120), p_img if p_img.mode == 'RGBA' else None)
        except:
            pass
        
    # Texte genau auf die Neymar-Karte angepasst (Farben und Positionen)
    # 1. Große Gesamtnote oben links (In coolem Weiß/Goldschimmer)
    draw.text((85, 125), f"{int(rating)}", fill="#ffffff", font_size=58, font_weight="bold")
    
    # 2. Position direkt unter der Note
    draw.text((85, 195), pos, fill="#a8ffda", font_size=26)
    
    # 3. Spielername fett zentriert im unteren Drittel
    draw.text((225, 375), name.upper(), fill="#ffffff", font_size=34, anchor="mm")
    
    # 4. Die 6 Stats-Zahlen (Genau über den Symbolen der Karte platziert)
    # Reihe 1: PAC, SHO, PAS
    draw.text((95, 465), f"{int(pac)}", fill="#ffffff", font_size=28, anchor="mm")
    draw.text((165, 465), f"{int(sho)}", fill="#ffffff", font_size=28, anchor="mm")
    draw.text((235, 465), f"{int(pas)}", fill="#ffffff", font_size=28, anchor="mm")
    
    # Reihe 2: DRI, DEF, PHY
    draw.text((305, 465), f"{int(dri)}", fill="#ffffff", font_size=28, anchor="mm")
    draw.text((375, 465), f"{int(def_stat)}", fill="#ffffff", font_size=28, anchor="mm")
    draw.text((445, 465), f"{int(phy)}", fill="#ffffff", font_size=28, anchor="mm")
    
    return card.convert("RGB")

# --- Navigation ---
st.title("🏆 Dein Club - Ultimate Team Manager")
menu = st.sidebar.radio("Navigation", ["Team-Übersicht & Karten", "Beste Start-Elf", "Spielplan", "Admin-Bereich"])

# --- Admin Authentifizierung ---
is_admin = st.sidebar.checkbox("Als Admin anmelden")
admin_authenticated = False
if is_admin:
    password = st.sidebar.text_input("Admin-Passwort", type="password")
    if password == "admin123":
        admin_authenticated = True
        st.sidebar.success("🔑 Admin-Modus aktiv!")
    else:
        st.sidebar.error("Falsches Passwort")

# --- 1. TEAM ÜBERSICHT ---
if menu == "Team-Übersicht & Karten":
    st.header("🏃‍♂️ Spielerkader & FUT-Karten")
    if not st.session_state.players:
        st.info("Noch keine Spieler eingetragen. Gehe in den Admin-Bereich, um dein Team anzulegen!")
    else:
        player_names = list(st.session_state.players.keys())
        selected_player = st.selectbox("Spieler auswählen für Detail-Fenster:", player_names)
        
        p = st.session_state.players[selected_player]
        
        col1, col2 = st.columns([1, 1])
        with col1:
            card_img = generate_fut_card(
                selected_player, p["rating"], p["main_pos"],
                p["pac"], p["sho"], p["pas"], p["dri"], p["def"], p["phy"],
                p.get("img_data")
            )
            st.image(card_img, use_container_width=True)
            
        with col2:
            st.subheader(f"Spielerprofil: {selected_player}")
            st.metric(label="Positions-Rating (OVR)", value=int(p["rating"]))
            st.write(f"**Hauptposition:** {p['main_pos']}")
            st.write(f"**Kann auch spielen:** {p['sub_pos']}")
            
            st.markdown("---")
            st.subheader("📊 Saison-Statistiken")
            c_t, c_a = st.columns(2)
            c_t.metric("⚽ Tore", p["goals"])
            c_a.metric("👟 Assists", p["assists"])

# --- 2. BESTE START-ELF ---
elif menu == "Beste Start-Elf":
    st.header("📋 KI-generierte Top-Aufstellung (4-3-3)")
    st.write("Die App wählt automatisch die Spieler mit dem höchsten angepassten Rating für die jeweilige Position aus.")
    
    positions_needed = {
        "TW": 1, "IV": 2, "LV": 1, "RV": 1,
        "ZM": 3, "ST": 1, "LF": 1, "RF": 1
    }
    
    available_players = []
    for name, data in st.session_state.players.items():
        all_positions = [data["main_pos"]] + [pos.strip() for pos in data["sub_pos"].split(",") if pos.strip()]
        available_players.append({"name": name, "rating": data["rating"], "positions": all_positions})
        
    df_players = pd.DataFrame(available_players)
    
    if len(df_players) < 11:
        st.warning("Du brauchst mindestens 11 Spieler im Kader, um eine Startelf zu berechnen!")
    else:
        df_players = df_players.sort_values(by="rating", ascending=False)
        lineup = {}
        assigned = set()
        
        for pos_type, count in positions_needed.items():
            lineup[pos_type] = []
            found = 0
            for idx, row in df_players.iterrows():
                if row["name"] not in assigned and pos_type in row["positions"]:
                    lineup[pos_type].append(f"{row['name']} ({int(row['rating'])})")
                    assigned.add(row["name"])
                    found += 1
                    if found == count:
                        break
            if found < count:
                for idx, row in df_players.iterrows():
                    if row["name"] not in assigned:
                        lineup[pos_type].append(f"{row['name']} ({int(row['rating'])}) [Ersatz]")
                        assigned.add(row["name"])
                        found += 1
                        if found == count:
                            break
                            
        st.subheader("⚽ Deine beste Elf auf dem Platz:")
        st.json(lineup)

# --- 3. SPIELPLAN ---
elif menu == "Spielplan":
    st.header("📅 Spielplan & Ergebnisse")
    if not st.session_state.matches:
        st.info("Es wurden noch keine Spiele eingetragen.")
    else:
        for idx, match in enumerate(st.session_state.matches):
            st.info(f"**Spieltag {idx+1}:** {match['date']} | **Gegner:** {match['opponent']} | **Ergebnis:** {match['result']}")

# --- 4. ADMIN-BEREICH ---
elif menu == "Admin-Bereich":
    st.header("⚡ Trainer-Zentrale (Admin)")
    if not admin_authenticated:
        st.warning("⚠️ Bitte aktiviere zuerst im linken Menü den Admin-Modus mit dem korrekten Passwort!")
    else:
        st.success("Erfolgreich als Admin verifiziert.")
        tab1, tab2, tab3 = st.tabs(["Spieler anlegen/bearbeiten", "Scorer & Stats eintragen", "Spielplan bearbeiten"])
        
        with tab1:
            st.subheader("➕ Neuen Spieler hinzufügen")
            with st.form("add_player_form"):
                p_name = st.text_input("Name des Spielers")
                m_pos = st.selectbox("Hauptposition", ["TW", "IV", "LV", "RV", "ZM", "ZDM", "ZOM", "LM", "RM", "ST", "LF", "RF"])
                s_pos = st.text_input("Nebenpositionen (mit Komma trennen, z.B. ZOM, LM)")
                
                st.write("**FUT-Kriterien (Werte von 1 bis 99):**")
                colA, colB, colC = st.columns(3)
                p_pac = colA.slider("Tempo / Kmh (PAC)", 1, 99, 50)
                p_sho = colB.slider("Schusskraft (SHO)", 1, 99, 50)
                p_pas = colC.slider("Übersicht / Passen (PAS)", 1, 99, 50)
                p_dri = colA.slider("Ballkontrolle / Dribbling (DRI)", 1, 99, 50)
                p_def = colB.slider("Verteidigung (DEF)", 1, 99, 50)
                p_phy = colC.slider("Physis / Ausdauer (PHY)", 1, 99, 50)
                
                p_img = st.file_uploader("Spieler-Foto hochladen", type=["png", "jpg", "jpeg"])
                
                submit = st.form_submit_button("Spieler im Team speichern")
                if submit and p_name:
                    ovr_rating = calculate_positional_rating(m_pos, p_pac, p_sho, p_pas, p_dri, p_def, p_phy)
                    
                    st.session_state.players[p_name] = {
                        "main_pos": m_pos, "sub_pos": s_pos,
                        "pac": p_pac, "sho": p_sho, "pas": p_pas,
                        "dri": p_dri, "def": p_def, "phy": p_phy,
