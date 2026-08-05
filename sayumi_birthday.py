import streamlit as st
import streamlit.components.v1 as components

import base64
import json
import re
import html as html_lib

st.set_page_config(page_title="Happy Birthday Sayumi", page_icon="🎂", layout="centered")
st.markdown("""
<style>
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

def img_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

photos = []
for i in range(1, 5):
    for ext in ['jpg','jpeg','png','webp']:
        b64 = img_to_b64(f"photo{i}.{ext}")
        if b64:
            photos.append(f"data:image/{ext};base64,{b64}")
            break
    else:
        photos.append(None)

# build JS array of photo srcs
photo_srcs = []
placeholders_emoji = ["📸","🌸","📸","🌺","🌷","💗"]
for i, src in enumerate(photos):
    if src:
        photo_srcs.append(f'"{src}"')
    else:
        photo_srcs.append(f'"__placeholder_{placeholders_emoji[i]}__"')
photo_srcs.append(f'"__placeholder_{placeholders_emoji[4]}__"')
photo_srcs.append(f'"__placeholder_{placeholders_emoji[5]}__"')
photo_srcs_js = "[" + ",".join(photo_srcs) + "]"

# load audio
audio_b64 = img_to_b64("sayumi_singing.ogg")
audio_src = f"data:audio/ogg;base64,{audio_b64}" if audio_b64 else ""

# load fun facts from facts.txt (same folder as this script)
# format, one per line:  1. <emoji> <text>
def load_facts(path="facts.txt"):
    default = [
        {"emoji": "🎆", "text": "u came a long way — from the quiet girl in cambridge 6 to the person who threatens to slap me daily. genuinely proud of this era."},
        {"emoji": "📝", "text": "u wrote me 4 pages. for no reason. tht says everything about who u are."},
        {"emoji": "🖤", "text": "the black fit era will never end. and honestly? it shouldn't."},
    ]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return default
    facts = []
    for line in raw_lines:
        m = re.match(r'^\d+\.\s*(\S+)\s+(.*)$', line)
        if m:
            facts.append({"emoji": m.group(1), "text": m.group(2).strip()})
    return facts if facts else default

fun_facts = load_facts()
fun_facts_js = json.dumps(fun_facts, ensure_ascii=False)

# load the birthday message from message.txt (same folder as this script)
# paragraphs separated by a blank line. the signature line is NOT part of
# this file — it stays fixed in the code.
def load_message(path="message.txt"):
    default = [
        "happy birthday sayumi 💗🎂 ur officially old now and i hope ur having the best time lmao. i still remember cambridge 6, the quiet nerd in the corner who wouldn't say a word to anyone, BUT NOT NOW OKK?? now she threatens to slap me every day and somehow tht's become one of my fav things about her 😭",
        "i need u to know tht never changed how much u mean to me. u wrote me 4 whole pages once for jz no reason and i still think about tht, cuz tht's jz who u are. u give so much without even thinking about it and i don't say this enough but i'm so glad to have u in my life. like actually glad, not jz saying it. u've been there through so much and i don't take tht for granted 🥹",
        "the kind of bsf tht checks on u, roasts u, threatens to hit u, and somehow still makes u feel like the luckiest person in the room 😂🫶",
        "have the best birthday okay. eat way too much cake.",
        "cheers to u being a bit older, more unbothered and still living in the same era as me 🎂🫶🥹",
    ]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
    except FileNotFoundError:
        return default
    if not raw:
        return default
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]
    return paragraphs if paragraphs else default

message_paragraphs = load_message()
message_paragraphs_js = json.dumps(message_paragraphs, ensure_ascii=False)

# load playlist from songs.txt (same folder as this script)
# format, one per line: N. title — artist | optional note
# audio files: song1.mp3, song2.mp3 ... (mp3/mp4/m4a/wav/ogg all work)
def load_songs(path="songs.txt"):
    default = [{"title": "must have been the wind", "artist": "", "note": ""}]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return default
    songs = []
    for line in raw_lines:
        m = re.match(r'^\d+\.\s*(.*)$', line)
        if not m:
            continue
        rest = m.group(1)
        note = ""
        if '|' in rest:
            rest, note = rest.split('|', 1)
            note = note.strip()
        rest = rest.strip()
        if '—' in rest:
            title, artist = rest.split('—', 1)
        elif ' - ' in rest:
            title, artist = rest.split(' - ', 1)
        else:
            title, artist = rest, ""
        songs.append({"title": title.strip(), "artist": artist.strip(), "note": note})
    return songs if songs else default

song_meta = load_songs()
_song_mime = {'mp3': 'audio/mpeg', 'mp4': 'video/mp4', 'm4a': 'audio/mp4', 'wav': 'audio/wav', 'ogg': 'audio/ogg'}
songs_data = []
for i, meta in enumerate(song_meta, start=1):
    src = None
    for ext in ['mp3', 'mp4', 'm4a', 'wav', 'ogg']:
        b64 = img_to_b64(f"song{i}.{ext}")
        if b64:
            src = f"data:{_song_mime[ext]};base64,{b64}"
            break
    songs_data.append({"title": meta["title"], "artist": meta["artist"], "note": meta["note"], "src": src, "n": i})
songs_js = json.dumps(songs_data, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}}
html,body{{touch-action:manipulation;}}
body{{font-family:'DM Sans',sans-serif;overflow:hidden;width:100vw;height:100vh;background:#fff0f5;}}
button,.key,.next-btn,.btn,.game-yes-btn,.btn-no,.nav-dot,.photo-stage,.play-btn,#progress-wrap,#tap-overlay{{touch-action:manipulation;}}
#confetti-canvas{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;}}
.hearts-bg{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:150;overflow:hidden;}}
.heart-float{{position:absolute;animation:floatUp linear infinite;opacity:0;}}
@keyframes floatUp{{0%{{transform:translateY(100vh) rotate(0deg);opacity:0.7;}}100%{{transform:translateY(-10vh) rotate(360deg);opacity:0;}}}}

/* PAGE SYSTEM */
.page{{
  position:fixed;top:0;left:0;width:100%;height:100%;
  display:flex;align-items:center;justify-content:center;
  flex-direction:column;
  transition:opacity 0.55s ease,transform 0.55s ease;
  opacity:0;pointer-events:none;transform:translateY(30px);
  z-index:100;padding:1.2rem 1.2rem 1.2rem;
  background:linear-gradient(135deg,#fff0f5 0%,#fef9ff 40%,#f0f4ff 100%);
  overflow-y:auto;
  gap:0.8rem;
}}
.page.active{{opacity:1;pointer-events:all;transform:translateY(0);}}
.page.exit-up{{opacity:0;transform:translateY(-40px);}}
.page.exit-down{{opacity:0;transform:translateY(40px);}}
#page-lock{{background:linear-gradient(135deg,#1a0f2e 0%,#2d1b4e 50%,#1a1035 100%);}}

/* scrollable page variant */
.page.scrollable{{
  align-items:center;
  justify-content:flex-start;
  padding-top:2rem;
  padding-bottom:2rem;
}}

/* NAV DOTS */
.nav-dots{{position:fixed;right:14px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:8px;z-index:200;}}
.nav-dot{{width:8px;height:8px;border-radius:50%;background:rgba(232,121,160,0.3);cursor:pointer;transition:background 0.3s ease,transform 0.3s ease;border:none;outline:none;}}
.nav-dot.active{{background:#e879a0;transform:scale(1.4);}}

/* NEXT BTN */
.next-btn{{background:linear-gradient(135deg,#e879a0,#a78bfa);color:white;border:none;border-radius:50px;padding:0.65rem 1.8rem;font-size:0.82rem;font-family:'DM Sans',sans-serif;font-weight:500;cursor:pointer;transition:transform 0.2s ease,box-shadow 0.2s ease;box-shadow:0 4px 20px rgba(232,121,160,0.3);flex-shrink:0;}}
.next-btn:hover{{transform:translateY(-3px) scale(1.04);box-shadow:0 8px 30px rgba(232,121,160,0.4);}}
.next-btn:active{{transform:scale(0.96);}}

/* TAP TO START OVERLAY */
#tap-overlay{{
  position:fixed;top:0;left:0;width:100%;height:100%;
  z-index:9000;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#1a0f2e 0%,#2d1b4e 50%,#1a1035 100%);
  gap:1rem;
}}
#tap-overlay.gone{{display:none;}}
.tap-emoji{{font-size:3rem;animation:float 2s ease-in-out infinite;}}
.tap-text{{font-family:'Playfair Display',serif;font-size:1.4rem;color:#f0abca;text-align:center;}}
.tap-sub{{font-size:0.75rem;color:#9d8fc0;letter-spacing:2px;text-transform:uppercase;text-align:center;}}
.tap-pulse{{
  width:60px;height:60px;border-radius:50%;
  border:2px solid #a78bfa;
  animation:tapPulse 1.5s ease-in-out infinite;
  display:flex;align-items:center;justify-content:center;
  font-size:1.5rem;
}}
@keyframes tapPulse{{
  0%,100%{{transform:scale(1);box-shadow:0 0 0 0 rgba(167,139,250,0.4);}}
  50%{{transform:scale(1.08);box-shadow:0 0 0 12px rgba(167,139,250,0);}}
}}
.lock-title{{font-family:'Playfair Display',serif;font-size:1.6rem;color:#f0abca;margin-bottom:0.3rem;text-align:center;}}
.lock-sub{{font-size:0.75rem;color:#9d8fc0;letter-spacing:2px;text-transform:uppercase;margin-bottom:1.5rem;text-align:center;}}
.pin-display{{display:flex;gap:12px;margin-bottom:1.5rem;justify-content:center;}}
.pin-dot{{width:16px;height:16px;border-radius:50%;border:2px solid #a78bfa;background:transparent;transition:background 0.2s ease,transform 0.15s ease;}}
.pin-dot.filled{{background:#e879a0;border-color:#e879a0;transform:scale(1.2);}}
.pin-dot.error{{background:#f87171;border-color:#f87171;animation:shake 0.4s ease;}}
@keyframes shake{{0%,100%{{transform:translateX(0);}}20%{{transform:translateX(-6px);}}40%{{transform:translateX(6px);}}60%{{transform:translateX(-4px);}}80%{{transform:translateX(4px);}}}}
.keypad{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;max-width:240px;width:100%;}}
.key{{background:rgba(255,255,255,0.07);border:1px solid rgba(167,139,250,0.25);border-radius:16px;padding:1rem;font-size:1.4rem;font-weight:500;color:#e8e0f0;cursor:pointer;text-align:center;transition:background 0.15s ease,transform 0.1s ease;font-family:'DM Sans',sans-serif;user-select:none;}}
.key:hover{{background:rgba(167,139,250,0.15);transform:scale(1.06);}}
.key:active{{transform:scale(0.93);background:rgba(232,121,160,0.2);}}
.key.del{{font-size:1rem;color:#a78bfa;}}
.key.empty{{visibility:hidden;}}
.lock-hint{{font-size:0.65rem;color:#6b5f80;margin-top:1.2rem;letter-spacing:1px;}}

/* HERO */
.hero-tag{{font-size:0.7rem;letter-spacing:3px;text-transform:uppercase;color:#c084a0;text-align:center;}}
.hero-name{{font-family:'Playfair Display',serif;font-size:clamp(3.5rem,12vw,6.5rem);font-weight:900;background:linear-gradient(135deg,#e879a0,#a78bfa,#60a5fa,#e879a0);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;animation:gradientShift 4s ease infinite;text-align:center;}}
@keyframes gradientShift{{0%,100%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}}}
.hero-sub{{font-size:1.05rem;color:#9d6b8a;font-weight:300;text-align:center;}}
.emoji-row{{text-align:center;font-size:1.6rem;letter-spacing:8px;animation:float 3s ease-in-out infinite;}}
@keyframes float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}

/* SECTION LABELS */
.section-label{{text-align:center;font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#c084a0;}}

/* COUNTDOWN */
.countdown-wrap{{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;}}
.cd-box{{background:white;border-radius:18px;padding:1rem 1.2rem;min-width:70px;text-align:center;box-shadow:0 4px 24px rgba(232,121,160,0.15);border:1px solid rgba(232,121,160,0.2);transition:transform 0.3s ease;cursor:default;}}
.cd-box:hover{{transform:translateY(-5px) scale(1.05);}}
.cd-num{{font-family:'Playfair Display',serif;font-size:2.2rem;font-weight:700;color:#e879a0;line-height:1;display:block;transition:transform 0.15s ease;}}
.cd-num.bump{{transform:scale(1.2);color:#a78bfa;}}
.cd-label{{font-size:0.6rem;text-transform:uppercase;letter-spacing:2px;color:#c084a0;margin-top:4px;display:block;}}
.bday-banner{{text-align:center;padding:1.5rem 2rem;background:linear-gradient(135deg,#fce7f0,#ede9fe,#dbeafe);border-radius:24px;animation:shimmer 3s ease-in-out infinite;width:100%;max-width:500px;}}
@keyframes shimmer{{0%,100%{{box-shadow:0 0 30px rgba(232,121,160,0.2);}}50%{{box-shadow:0 0 60px rgba(167,139,250,0.4);}}}}
.bday-title{{font-family:'Playfair Display',serif;font-size:2.2rem;background:linear-gradient(135deg,#e879a0,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:float 2s ease-in-out infinite;}}

/* BUTTONS */
.btn-row{{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;}}
.btn{{border:none;border-radius:50px;padding:0.65rem 1.4rem;font-size:0.8rem;font-family:'DM Sans',sans-serif;font-weight:500;cursor:pointer;transition:transform 0.2s ease,box-shadow 0.2s ease;}}
.btn-primary{{background:linear-gradient(135deg,#e879a0,#a78bfa);color:white;box-shadow:0 4px 20px rgba(232,121,160,0.3);}}
.btn-primary:hover{{transform:translateY(-3px) scale(1.04);box-shadow:0 8px 30px rgba(232,121,160,0.4);}}
.btn-primary:active{{transform:scale(0.96);}}
.btn-outline{{background:white;color:#e879a0;border:2px solid #e879a0;}}
.btn-outline:hover{{background:#fff0f5;transform:translateY(-3px);}}
.btn-dev{{background:#1e1e2e;color:#a78bfa;border:1px dashed #a78bfa55;font-size:0.7rem;padding:0.55rem 1rem;}}
.btn-dev:hover{{background:#2a2440;transform:translateY(-2px);}}
.dev-badge{{display:inline-block;background:#1e1e2e;color:#a78bfa;font-size:0.6rem;font-family:monospace;padding:2px 6px;border-radius:4px;margin-left:4px;border:1px solid #a78bfa44;}}

/* ROAST */
.fact-card{{background:linear-gradient(135deg,#fdf2f8,#faf5ff);border-radius:20px;padding:1.2rem 1.5rem;text-align:center;border:1px solid rgba(232,121,160,0.15);transition:opacity 0.3s ease,transform 0.3s ease;min-height:100px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;width:100%;max-width:500px;}}
.fact-card.switching{{opacity:0;transform:scale(0.95);}}
.fact-emoji{{font-size:2rem;}}
.fact-text{{color:#6b4f6b;font-size:0.88rem;line-height:1.7;}}
.fact-counter{{color:#c084a0;font-size:0.62rem;letter-spacing:1px;}}

/* PHOTO SLIDESHOW */
.photo-stage{{position:relative;width:100%;max-width:340px;aspect-ratio:1;border-radius:24px;overflow:hidden;cursor:pointer;box-shadow:0 12px 40px rgba(232,121,160,0.2);flex-shrink:0;}}
.photo-slide{{position:absolute;top:0;left:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;transition:opacity 0.5s ease,transform 0.5s ease;}}
.photo-slide img{{width:100%;height:100%;object-fit:cover;border-radius:24px;}}
.photo-slide .ph{{width:100%;height:100%;background:linear-gradient(135deg,#fce7f0,#ede9fe);display:flex;align-items:center;justify-content:center;font-size:3.5rem;border-radius:24px;border:2px dashed rgba(232,121,160,0.3);}}
.photo-slide.hidden{{opacity:0;transform:scale(0.92);pointer-events:none;}}
.photo-dots{{display:flex;gap:6px;justify-content:center;}}
.photo-dot{{width:7px;height:7px;border-radius:50%;background:rgba(232,121,160,0.3);transition:background 0.3s ease,transform 0.3s ease;}}
.photo-dot.active{{background:#e879a0;transform:scale(1.3);}}
.photo-hint{{font-size:0.65rem;color:#c084a0;letter-spacing:1px;}}

/* GAME */
.game-wrap{{width:100%;max-width:480px;background:white;border-radius:24px;padding:1.5rem;text-align:center;box-shadow:0 8px 40px rgba(232,121,160,0.12);border:1px solid rgba(232,121,160,0.18);}}
.game-question{{font-family:'Playfair Display',serif;font-size:1.15rem;color:#6b4f6b;margin-bottom:0.3rem;}}
.game-sub{{font-size:0.73rem;color:#c084a0;letter-spacing:1px;margin-bottom:0.8rem;}}
.game-arena{{position:relative;width:100%;height:140px;border:2px dashed rgba(232,121,160,0.25);border-radius:16px;overflow:hidden;background:linear-gradient(135deg,#fdf2f8,#faf5ff);}}
.game-yes-btn{{background:linear-gradient(135deg,#e879a0,#a78bfa);color:white;border:none;border-radius:50px;padding:0.65rem 1.6rem;font-size:0.82rem;font-family:'DM Sans',sans-serif;font-weight:500;cursor:pointer;box-shadow:0 4px 20px rgba(232,121,160,0.3);position:absolute;left:25%;top:50%;transform:translate(-50%,-50%);transition:transform 0.15s ease;z-index:2;}}
.game-yes-btn:hover{{transform:translate(-50%,-50%) scale(1.08);}}
.game-yes-btn:active{{transform:translate(-50%,-50%) scale(0.95);}}
.btn-no{{background:white;color:#9d6b8a;border:2px solid #e0b4c8;border-radius:50px;padding:0.65rem 1.4rem;font-size:0.82rem;font-family:'DM Sans',sans-serif;font-weight:500;cursor:pointer;position:absolute;white-space:nowrap;transition:left 0.4s cubic-bezier(.25,.46,.45,.94),top 0.4s cubic-bezier(.25,.46,.45,.94),font-size 0.2s ease;left:70%;top:50%;transform:translate(-50%,-50%);}}
.game-result{{font-size:1rem;color:#e879a0;font-family:'Playfair Display',serif;margin-top:0.8rem;animation:popIn 0.4s ease both;display:none;}}
@keyframes popIn{{from{{opacity:0;transform:scale(0.8);}}to{{opacity:1;transform:scale(1);}}}}

/* FUN FACTS about her - scattered layout, count driven by facts.txt */
.fun-facts-scatter{{width:100%;max-width:520px;display:flex;flex-wrap:wrap;justify-content:center;align-content:center;gap:0.9rem;padding:0.5rem;}}
.fun-fact-card{{background:white;border-radius:20px;padding:1.2rem 1.4rem;text-align:center;box-shadow:0 4px 24px rgba(167,139,250,0.12);border:1px solid rgba(167,139,250,0.15);width:150px;animation:fadeSlideUp 0.5s ease both;transition:transform 0.25s ease;}}
.fun-fact-card:hover{{transform:rotate(0deg) scale(1.04) !important;}}
.fun-fact-emoji{{font-size:2.2rem;margin-bottom:0.4rem;}}
.fun-fact-text{{font-size:0.8rem;color:#6b4f6b;line-height:1.5;}}

/* MESSAGE */
.msg-wrap{{width:100%;max-width:500px;background:white;border-radius:24px;padding:1.8rem;box-shadow:0 8px 40px rgba(167,139,250,0.12);border:1px solid rgba(167,139,250,0.18);}}
.msg-quote{{font-size:3rem;color:#f0abca;font-family:'Playfair Display',serif;line-height:0.5;margin-bottom:1rem;}}
.msg-text{{font-size:0.88rem;line-height:1.95;color:#6b4f6b;font-weight:300;}}
.msg-sign{{margin-top:1.2rem;font-family:'Playfair Display',serif;font-style:italic;color:#c084a0;font-size:0.95rem;}}

/* AUDIO PLAYER */
.audio-card{{background:white;border-radius:24px;padding:1.8rem;width:100%;max-width:480px;box-shadow:0 8px 40px rgba(232,121,160,0.15);border:1px solid rgba(232,121,160,0.2);text-align:center;}}
.audio-title{{font-family:'Playfair Display',serif;font-size:1.2rem;color:#6b4f6b;margin-bottom:0.2rem;}}
.audio-sub{{font-size:0.75rem;color:#c084a0;letter-spacing:1px;margin-bottom:1.5rem;}}
.audio-visualizer{{display:flex;align-items:flex-end;justify-content:center;gap:4px;height:48px;margin-bottom:1.2rem;}}
.audio-bar{{width:6px;border-radius:3px;background:linear-gradient(to top,#e879a0,#a78bfa);transition:height 0.15s ease;height:6px;}}
.audio-bar.active{{animation:barBounce 0.6s ease-in-out infinite;}}
.audio-bar:nth-child(2){{animation-delay:0.1s;}}
.audio-bar:nth-child(3){{animation-delay:0.2s;}}
.audio-bar:nth-child(4){{animation-delay:0.05s;}}
.audio-bar:nth-child(5){{animation-delay:0.15s;}}
.audio-bar:nth-child(6){{animation-delay:0.25s;}}
.audio-bar:nth-child(7){{animation-delay:0.08s;}}
.audio-bar:nth-child(8){{animation-delay:0.18s;}}
@keyframes barBounce{{0%,100%{{height:6px;}}50%{{height:36px;}}}}
.audio-controls{{display:flex;align-items:center;gap:12px;justify-content:center;margin-bottom:1rem;}}
.play-btn{{width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#e879a0,#a78bfa);border:none;color:white;font-size:1.4rem;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px rgba(232,121,160,0.35);transition:transform 0.2s ease,box-shadow 0.2s ease;}}
.play-btn:hover{{transform:scale(1.08);box-shadow:0 8px 30px rgba(232,121,160,0.45);}}
.play-btn:active{{transform:scale(0.95);}}
.audio-progress-wrap{{width:100%;background:#fce7f0;border-radius:10px;height:6px;cursor:pointer;position:relative;}}
.audio-progress-fill{{height:100%;border-radius:10px;background:linear-gradient(90deg,#e879a0,#a78bfa);width:0%;transition:width 0.3s linear;}}
.audio-times{{display:flex;justify-content:space-between;font-size:0.65rem;color:#c084a0;font-family:monospace;margin-top:4px;}}
.audio-label{{font-size:0.72rem;color:#9d6b8a;margin-top:0.8rem;font-style:italic;}}

/* ENDING */
.ending-wrap{{text-align:center;width:100%;max-width:500px;}}
.ending-big{{font-family:'Playfair Display',serif;font-size:clamp(2rem,8vw,3.5rem);font-weight:900;background:linear-gradient(135deg,#e879a0,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:gradientShift 3s ease infinite;margin-bottom:0.5rem;}}
.ending-sub{{color:#9d6b8a;font-size:0.88rem;line-height:1.7;margin-bottom:1rem;}}

/* RATE ME */
.rate-wrap{{width:100%;max-width:460px;display:flex;flex-direction:column;gap:1rem;}}
.stat-row{{background:white;border-radius:16px;padding:0.9rem 1.1rem;box-shadow:0 4px 20px rgba(232,121,160,0.1);border:1px solid rgba(232,121,160,0.12);}}
.stat-top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;}}
.stat-label{{font-size:0.75rem;color:#6b4f6b;text-transform:uppercase;letter-spacing:1px;font-weight:500;}}
.stat-score{{font-family:'Playfair Display',serif;color:#e879a0;font-weight:700;font-size:0.9rem;flex-shrink:0;margin-left:0.6rem;}}
.stat-bar{{width:100%;height:8px;background:#fce7f0;border-radius:6px;overflow:hidden;}}
.stat-fill{{height:100%;width:0%;background:linear-gradient(90deg,#e879a0,#a78bfa);border-radius:6px;transition:width 0.8s cubic-bezier(.25,.46,.45,.94);}}
.stat-caption{{font-size:0.7rem;color:#9d6b8a;margin-top:0.4rem;font-style:italic;}}

/* PLAYLIST */
.playlist-wrap{{width:100%;max-width:460px;display:flex;flex-direction:column;gap:0.75rem;}}
.track-card{{background:white;border-radius:18px;padding:0.85rem 1.05rem;display:flex;align-items:center;gap:0.85rem;box-shadow:0 4px 20px rgba(232,121,160,0.1);border:1px solid rgba(232,121,160,0.12);}}
.track-play-btn{{flex-shrink:0;width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#e879a0,#a78bfa);border:none;color:white;font-size:0.95rem;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px rgba(232,121,160,0.3);}}
.track-info{{flex:1;min-width:0;text-align:left;}}
.track-title{{font-family:'Playfair Display',serif;font-size:0.92rem;color:#6b4f6b;}}
.track-artist{{font-size:0.68rem;color:#c084a0;margin-top:1px;}}
.track-note{{font-size:0.68rem;color:#9d6b8a;font-style:italic;margin-top:2px;}}
.track-missing{{font-size:0.62rem;color:#d6b9c6;margin-top:4px;}}
.track-progress-wrap{{width:100%;background:#fce7f0;border-radius:8px;height:5px;cursor:pointer;margin-top:6px;}}
.track-progress-fill{{height:100%;width:0%;background:linear-gradient(90deg,#e879a0,#a78bfa);border-radius:8px;transition:width 0.2s linear;}}

.footer{{font-size:0.7rem;color:#c084a0;letter-spacing:1px;text-align:center;}}
@keyframes fadeSlideUp{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
</style>
</head>
<body>
<canvas id="confetti-canvas"></canvas>
<div class="hearts-bg" id="hearts-bg"></div>

<div class="nav-dots" id="nav-dots" style="display:none">
  <button class="nav-dot" onclick="goTo(1)"></button>
  <button class="nav-dot" onclick="goTo(2)"></button>
  <button class="nav-dot" onclick="goTo(3)"></button>
  <button class="nav-dot" onclick="goTo(4)"></button>
  <button class="nav-dot" onclick="goTo(5)"></button>
  <button class="nav-dot" onclick="goTo(6)"></button>
  <button class="nav-dot" onclick="goTo(7)"></button>
  <button class="nav-dot" onclick="goTo(8)"></button>
  <button class="nav-dot" onclick="goTo(9)"></button>
  <button class="nav-dot" onclick="goTo(10)"></button>
</div>

<!-- TAP OVERLAY -->
<div id="tap-overlay">
  <div class="tap-emoji">&#127383;</div>
  <div class="tap-text">tap anywhere to open</div>
  <div class="tap-sub">something special is waiting</div>
  <div class="tap-pulse">&#10024;</div>
</div>

<!-- PAGE 0: LOCK -->
<div class="page active" id="page-lock">
  <div class="lock-title">&#127383; hey sayumi &#127383;</div>
  <div class="lock-sub">enter the secret code</div>
  <div class="pin-display" id="pin-display">
    <div class="pin-dot" id="d0"></div><div class="pin-dot" id="d1"></div>
    <div class="pin-dot" id="d2"></div><div class="pin-dot" id="d3"></div>
    <div class="pin-dot" id="d4"></div><div class="pin-dot" id="d5"></div>
    <div class="pin-dot" id="d6"></div><div class="pin-dot" id="d7"></div>
  </div>
  <div class="keypad">
    <div class="key" onclick="pressKey('1')">1</div>
    <div class="key" onclick="pressKey('2')">2</div>
    <div class="key" onclick="pressKey('3')">3</div>
    <div class="key" onclick="pressKey('4')">4</div>
    <div class="key" onclick="pressKey('5')">5</div>
    <div class="key" onclick="pressKey('6')">6</div>
    <div class="key" onclick="pressKey('7')">7</div>
    <div class="key" onclick="pressKey('8')">8</div>
    <div class="key" onclick="pressKey('9')">9</div>
    <div class="key empty"></div>
    <div class="key" onclick="pressKey('0')">0</div>
    <div class="key del" onclick="deleteKey()">&#9003;</div>
  </div>
  <div class="lock-hint">hint: her bday &#128521;</div>
</div>

<!-- PAGE 1: HERO -->
<div class="page" id="page-hero">
  <div class="hero-tag">&#10022; a little something for you &#10022;</div>
  <div class="hero-name">Sayumi</div>
  <div class="hero-sub">turning 14 &middot; august 6th &#10024;</div>
  <div class="emoji-row">&#127874; &#128151; &#127881; &#129782; &#129401;</div>
  <button class="next-btn" onclick="goTo(2)">open &#128151;</button>
</div>

<!-- PAGE 2: COUNTDOWN -->
<div class="page" id="page-countdown">
  <div id="countdown-inner" style="width:100%;display:flex;flex-direction:column;align-items:center;gap:0.8rem;">
    <div class="section-label">countdown to the big day &#127872;</div>
    <div class="countdown-wrap">
      <div class="cd-box"><span class="cd-num" id="cd-days">--</span><span class="cd-label">Days</span></div>
      <div class="cd-box"><span class="cd-num" id="cd-hours">--</span><span class="cd-label">Hours</span></div>
      <div class="cd-box"><span class="cd-num" id="cd-mins">--</span><span class="cd-label">Minutes</span></div>
      <div class="cd-box"><span class="cd-num" id="cd-secs">--</span><span class="cd-label">Seconds</span></div>
    </div>
  </div>
  <div id="bday-inner" style="display:none;width:100%;max-width:500px;">
    <div class="bday-banner">
      <div class="bday-title">&#127874; IT'S YOUR DAY!! &#127874;</div>
      <p style="color:#9d6b8a;margin-top:0.8rem;">Happy Birthday Sayumi &#128151;</p>
    </div>
  </div>
  <div class="btn-row">
    <button class="btn btn-primary" onclick="launchConfetti()">&#127881; Confetti!</button>
    <button class="btn btn-primary" onclick="heartShower()">&#128151; Hearts</button>
    <button class="btn btn-dev" onclick="devMode()">&#9881;&#65039; dev 10s <span class="dev-badge">DEV</span></button>
  </div>
  <button class="next-btn" onclick="goTo(3)">next &#128151;</button>
</div>

<!-- PAGE 3: PHOTOS -->
<div class="page" id="page-photos">
  <div class="section-label">ur camera roll era &#128248;</div>
  <div class="photo-stage" id="photo-stage" onclick="nextPhoto()">
    <div id="photo-slides"></div>
  </div>
  <div class="photo-dots" id="photo-dots"></div>
  <div class="photo-hint">tap to go to next pic &#128247;</div>
  <button class="next-btn" onclick="goTo(4)">next &#128151;</button>
</div>

<!-- PAGE 5: GAME -->
<div class="page" id="page-game">
  <div class="game-wrap">
    <div class="game-question" id="game-question">ur old now aren't u? &#128514;</div>
    <div class="game-sub" id="game-sub">choose wisely</div>
    <div class="game-arena" id="game-arena">
      <button class="game-yes-btn" id="yes-btn" onclick="yesClicked()">yes &#128151;</button>
      <button class="btn-no" id="no-btn">no</button>
    </div>
    <div class="game-result" id="game-result"></div>
  </div>
  <button class="next-btn" onclick="goTo(5)" style="margin-top:0.8rem;">read my msg &#128140;</button>
</div>

<!-- PAGE 6: MESSAGE (scrollable) -->
<div class="page scrollable" id="page-msg">
  <div class="msg-wrap">
    <div class="msg-quote">"</div>
    <div class="msg-text" id="msg-text-body"></div>
    <div class="msg-sign">— ur bsf, always &#128151;</div>
  </div>
  <button class="next-btn" onclick="goTo(6)" style="flex-shrink:0;">almost done &#129782;</button>
</div>

<!-- PAGE 7: FUN FACTS about Sayumi -->
<div class="page" id="page-facts">
  <div class="section-label">some things about u &#129401;</div>
  <div id="fun-facts-wrap" class="fun-facts-scatter"></div>
  <button class="next-btn" onclick="goTo(7)">next &#127874;</button>
</div>

<!-- PAGE: RATE ME -->
<div class="page" id="page-rate">
  <div class="section-label">rate ur bestie (by me, 100% unbiased) &#128202;</div>
  <div class="rate-wrap" id="rate-wrap"></div>
  <button class="next-btn" onclick="goTo(8)">next &#128151;</button>
</div>

<!-- PAGE: PLAYLIST -->
<div class="page" id="page-playlist">
  <div class="section-label">songs tht remind me of u &#127925;</div>
  <div class="playlist-wrap" id="playlist-wrap"></div>
  <button class="next-btn" onclick="goTo(9)">wait... one more &#128064;</button>
</div>

<!-- PAGE: HER SONG (bonus reveal) -->
<div class="page" id="page-audio">
  <div class="section-label">oh sh*t... one more song &#128064;<br><span style="font-size:0.85em;opacity:0.85;">and it's her singing &#127908;</span></div>
  <div class="audio-card">
    <div class="audio-title">&#127925; Infected</div>
    <div class="audio-sub">featuring: sayumi live &#127908;</div>
    <div class="audio-visualizer" id="visualizer">
      <div class="audio-bar"></div><div class="audio-bar"></div>
      <div class="audio-bar"></div><div class="audio-bar"></div>
      <div class="audio-bar"></div><div class="audio-bar"></div>
      <div class="audio-bar"></div><div class="audio-bar"></div>
    </div>
    <div class="audio-controls">
      <button class="play-btn" id="play-btn" onclick="togglePlay()">&#9654;&#65039;</button>
    </div>
    <div class="audio-progress-wrap" id="progress-wrap" onclick="seekAudio(event)">
      <div class="audio-progress-fill" id="progress-fill"></div>
    </div>
    <div class="audio-times">
      <span id="cur-time">0:00</span>
      <span id="dur-time">0:00</span>
    </div>
    <div class="audio-label">she actually sang this &#128557;&#128151;</div>
  </div>
  <audio id="sayu-audio" src="{audio_src}" preload="metadata"></audio>
  <button class="next-btn" onclick="goTo(10)" style="margin-top:0.8rem;">last page &#127874;</button>
</div>

<!-- PAGE 9: ENDING -->
<div class="page" id="page-ending">
  <div class="ending-wrap">
    <div class="ending-big">Happy Birthday &#127874;</div>
    <div class="ending-sub">
      this only happens once a year.<br>
      hope u make it count.<br>
      eat cake. be unbothered.<br>
      that's the whole plan. &#128151;
    </div>
    <div class="btn-row" style="justify-content:center;margin-bottom:1rem;">
      <button class="btn btn-primary" onclick="launchConfetti()">&#127881; one last confetti</button>
      <button class="btn btn-primary" onclick="heartShower()">&#128151; heart shower</button>
    </div>
    <div class="footer">made with &#128151; &middot; for sayumi &middot; august 6th 2026</div>
  </div>
</div>

<script>
// ---- TOUCH RELIABILITY FIX ----
// Inside a nested Streamlit iframe, mobile browsers can delay or drop the
// synthetic 'click' that normally follows a touch (partly to detect
// double-tap-to-zoom). That's what makes buttons feel unresponsive.
// Fix: on touchend, immediately fire the click ourselves instead of
// waiting for the browser to translate the touch on its own.
const TAP_SELECTOR = '.key,.next-btn,.btn,.game-yes-btn,.btn-no,.nav-dot,.photo-stage,.play-btn,.audio-progress-wrap,#tap-overlay,.track-play-btn,.track-progress-wrap';
document.addEventListener('touchend', function(e) {{
  const target = e.target.closest(TAP_SELECTOR);
  if (!target) return;
  e.preventDefault();
  if (target.classList.contains('audio-progress-wrap') || target.classList.contains('track-progress-wrap')) {{
    const t = e.changedTouches[0];
    target.dispatchEvent(new MouseEvent('click', {{clientX: t ? t.clientX : 0, bubbles: true, cancelable: true}}));
  }} else {{
    target.click();
  }}
}}, {{passive: false}});

document.addEventListener('DOMContentLoaded', () => {{
  const overlay = document.getElementById('tap-overlay');
  if (overlay) {{
    overlay.addEventListener('click', () => {{
      overlay.classList.add('gone');
      document.body.focus();
    }}, {{once: true}});
  }}
}});

// ---- PAGE SYSTEM ----
let currentPage = 0;
const pageIds = ['page-lock','page-hero','page-countdown','page-photos','page-game','page-msg','page-facts','page-rate','page-playlist','page-audio','page-ending'];
const totalNavPages = 10;

function goTo(idx) {{
  const prev = document.getElementById(pageIds[currentPage]);
  const next = document.getElementById(pageIds[idx]);
  const goingForward = idx > currentPage;
  prev.classList.remove('active');
  prev.classList.add(goingForward ? 'exit-up' : 'exit-down');
  setTimeout(() => {{ prev.classList.remove('exit-up','exit-down'); }}, 600);
  // scroll to top for scrollable pages
  next.scrollTop = 0;
  next.classList.add('active');
  currentPage = idx;
  const dots = document.querySelectorAll('.nav-dot');
  dots.forEach((d,i) => d.classList.toggle('active', i === idx - 1));
  if (idx > 0) document.getElementById('nav-dots').style.display = 'flex';
  if (pageIds[idx] === 'page-rate') setTimeout(animateRateStats, 60);
}}

// ---- LOCK ----
const PASSWORD = '06082012';
let pin = '';
function pressKey(k) {{
  if (pin.length >= 8) return;
  pin += k; updateDots();
  if (pin.length === 8) setTimeout(() => {{ pin === PASSWORD ? unlockSuccess() : wrongPin(); }}, 150);
}}
function deleteKey() {{ pin = pin.slice(0,-1); updateDots(); }}
function updateDots() {{
  for (let i=0;i<8;i++) {{
    const d = document.getElementById('d'+i);
    d.classList.toggle('filled', i < pin.length);
    d.classList.remove('error');
  }}
}}
function wrongPin() {{
  for (let i=0;i<8;i++) document.getElementById('d'+i).classList.add('error');
  setTimeout(() => {{ pin=''; updateDots(); }}, 600);
}}
function unlockSuccess() {{
  launchConfetti();
  setTimeout(() => goTo(1), 400);
}}

// ---- FLOATING HEARTS ----
const heartsBg = document.getElementById('hearts-bg');
const heartEmojis = ['&#128151;','&#127800;','&#128156;','&#10024;','&#127872;','&#128149;','&#127801;','&#128171;'];
for (let i=0;i<16;i++) spawnHeart(true);
function spawnHeart(initial) {{
  const h = document.createElement('div');
  h.className = 'heart-float';
  h.innerHTML = heartEmojis[Math.floor(Math.random()*heartEmojis.length)];
  h.style.left = Math.random()*100+'vw';
  const dur = 7+Math.random()*10;
  h.style.animationDuration = dur+'s';
  h.style.animationDelay = (initial?Math.random()*8:0)+'s';
  h.style.fontSize = (0.8+Math.random()*1.2)+'rem';
  heartsBg.appendChild(h);
  setTimeout(() => {{ h.remove(); spawnHeart(false); }}, (dur+(initial?Math.random()*8:0))*1000);
}}

// ---- CONFETTI ----
const canvas = document.getElementById('confetti-canvas');
const ctx = canvas.getContext('2d');
function resizeCanvas() {{ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }}
resizeCanvas(); window.addEventListener('resize', resizeCanvas);
let pieces=[], animId=null, fadeTimer=null;
function launchConfetti() {{
  if (fadeTimer) {{ clearTimeout(fadeTimer); fadeTimer=null; }}
  const colors=['#e879a0','#a78bfa','#60a5fa','#fbbf24','#34d399','#f472b6','#fb923c'];
  for (let i=0;i<180;i++) {{
    pieces.push({{x:Math.random()*canvas.width,y:-20-Math.random()*100,w:6+Math.random()*8,h:10+Math.random()*8,
      color:colors[Math.floor(Math.random()*colors.length)],speed:2+Math.random()*4,
      drift:(Math.random()-0.5)*2,spin:(Math.random()-0.5)*0.15,angle:Math.random()*Math.PI*2,opacity:0.85,fading:false}});
  }}
  if (!animId) animateConfetti();
  fadeTimer = setTimeout(() => {{ pieces.forEach(p=>p.fading=true); }}, 4000);
}}
function animateConfetti() {{
  ctx.clearRect(0,0,canvas.width,canvas.height);
  pieces = pieces.filter(p=>p.opacity>0.01&&p.y<canvas.height+30);
  pieces.forEach(p=>{{
    p.y+=p.speed;p.x+=p.drift;p.angle+=p.spin;
    if(p.fading) p.opacity=Math.max(0,p.opacity-0.025);
    ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.angle);
    ctx.globalAlpha=p.opacity;ctx.fillStyle=p.color;
    ctx.fillRect(-p.w/2,-p.h/2,p.w,p.h);ctx.restore();
  }});
  if(pieces.length>0) animId=requestAnimationFrame(animateConfetti);
  else {{ animId=null; ctx.clearRect(0,0,canvas.width,canvas.height); }}
}}
function heartShower() {{
  for(let i=0;i<30;i++) setTimeout(()=>spawnHeart(false), i*60);
}}

// ---- COUNTDOWN ----
let devOffset=0,devActive=false,bdayTriggered=false;
function devMode(){{
  const now=new Date(); const bday=getNextBirthday();
  devOffset=Math.floor((bday-now)/1000)-10;
  devActive=true; bdayTriggered=false; updateCountdown();
}}
function getNextBirthday(){{
  const now=new Date();
  let bday=new Date(now.getFullYear(),7,6,0,0,0);
  if(now>=bday) bday.setFullYear(bday.getFullYear()+1);
  return bday;
}}
function updateCountdown(){{
  const now=new Date(); const bday=getNextBirthday();
  let diff=Math.floor((bday-now)/1000)-(devActive?devOffset:0);
  if(diff<=0){{
    document.getElementById('countdown-inner').style.display='none';
    document.getElementById('bday-inner').style.display='block';
    if(!bdayTriggered){{bdayTriggered=true;launchConfetti();setTimeout(()=>launchConfetti(),600);}}
    return;
  }}
  bdayTriggered=false;
  document.getElementById('countdown-inner').style.display='flex';
  document.getElementById('bday-inner').style.display='none';
  setNum('cd-days',Math.floor(diff/86400));
  setNum('cd-hours',Math.floor((diff%86400)/3600));
  setNum('cd-mins',Math.floor((diff%3600)/60));
  setNum('cd-secs',diff%60);
}}
let prevVals={{}};
function setNum(id,val){{
  const el=document.getElementById(id);
  const str=String(val).padStart(2,'0');
  if(prevVals[id]!==str){{el.classList.add('bump');setTimeout(()=>el.classList.remove('bump'),150);prevVals[id]=str;}}
  el.textContent=str;
}}
updateCountdown(); setInterval(updateCountdown,1000);

// ---- RATE ME ----
const rateStats = [
  {{label:'reply speed', score:3, caption:'somewhere between instant and 3 business days'}},
  {{label:'meme game', score:9, caption:'certified menace'}},
  {{label:'chaos energy', score:10, caption:'unmatched, no notes'}},
  {{label:'slap threat frequency', score:10, caption:'daily. consistent. reliable.'}},
  {{label:'roast accuracy', score:8, caption:'hurts cuz its true'}},
  {{label:'overall bestie rating', score:11, caption:'off the charts, no competition'}},
];
const rateWrap = document.getElementById('rate-wrap');
rateStats.forEach((s,i) => {{
  const row = document.createElement('div');
  row.className = 'stat-row';
  row.innerHTML =
    '<div class="stat-top"><span class="stat-label">'+s.label+'</span><span class="stat-score">'+s.score+'/10</span></div>'+
    '<div class="stat-bar"><div class="stat-fill" id="stat-fill-'+i+'"></div></div>'+
    '<div class="stat-caption">'+s.caption+'</div>';
  rateWrap.appendChild(row);
}});
let rateAnimated = false;
function animateRateStats(){{
  if (rateAnimated) return;
  rateAnimated = true;
  rateStats.forEach((s,i) => {{
    const fill = document.getElementById('stat-fill-'+i);
    if(fill) setTimeout(()=>{{ fill.style.width = Math.min(s.score,10)*10+'%'; }}, 80*i);
  }});
}}

// ---- PLAYLIST ----
const playlistSongs = {songs_js};
const playlistWrap = document.getElementById('playlist-wrap');
let currentPlayingTrack = null;
playlistSongs.forEach((song,i) => {{
  const card = document.createElement('div');
  card.className = 'track-card';
  const artistHtml = song.artist ? '<div class="track-artist">'+song.artist+'</div>' : '';
  const noteHtml = song.note ? '<div class="track-note">'+song.note+'</div>' : '';
  const barHtml = song.src
    ? '<div class="track-progress-wrap" id="track-progress-wrap-'+i+'"><div class="track-progress-fill" id="track-progress-fill-'+i+'"></div></div>'
    : '<div class="track-missing">add song'+song.n+'.mp3 to enable playback</div>';
  card.innerHTML =
    '<button class="track-play-btn" id="track-play-'+i+'">&#9654;&#65039;</button>'+
    '<div class="track-info">'+
      '<div class="track-title">'+song.title+'</div>'+
      artistHtml + noteHtml + barHtml +
    '</div>';
  playlistWrap.appendChild(card);

  if (song.src) {{
    const trackAudio = new Audio(song.src);
    const playBtnEl = card.querySelector('#track-play-'+i);
    const progWrap = card.querySelector('#track-progress-wrap-'+i);
    const progFill = card.querySelector('#track-progress-fill-'+i);
    playBtnEl.addEventListener('click', () => {{
      if (currentPlayingTrack && currentPlayingTrack !== trackAudio) currentPlayingTrack.pause();
      if (trackAudio.paused) {{
        trackAudio.play();
        playBtnEl.innerHTML = '&#9646;&#9646;';
        currentPlayingTrack = trackAudio;
      }} else {{
        trackAudio.pause();
        playBtnEl.innerHTML = '&#9654;&#65039;';
      }}
    }});
    trackAudio.addEventListener('pause', () => {{ playBtnEl.innerHTML = '&#9654;&#65039;'; }});
    trackAudio.addEventListener('play', () => {{ playBtnEl.innerHTML = '&#9646;&#9646;'; }});
    trackAudio.addEventListener('timeupdate', () => {{
      if (trackAudio.duration) progFill.style.width = (trackAudio.currentTime/trackAudio.duration*100)+'%';
    }});
    trackAudio.addEventListener('ended', () => {{ progFill.style.width = '0%'; }});
    progWrap.addEventListener('click', (e) => {{
      if (!trackAudio.duration) return;
      const rect = progWrap.getBoundingClientRect();
      const pct = (e.clientX - rect.left) / rect.width;
      trackAudio.currentTime = Math.min(Math.max(pct,0),1) * trackAudio.duration;
    }});
  }}
}});

// ---- BIRTHDAY MESSAGE (driven by message.txt) ----
const messageParagraphs = {message_paragraphs_js};
function escapeHtml(s){{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
document.getElementById('msg-text-body').innerHTML =
  messageParagraphs.map(p => escapeHtml(p)).join('<br><br>');

// ---- FUN FACTS (scattered, driven by facts.txt) ----
const funFacts = {fun_facts_js};
const funFactsWrap = document.getElementById('fun-facts-wrap');
funFacts.forEach((f,i) => {{
  const card = document.createElement('div');
  card.className = 'fun-fact-card';
  const rot = (i % 2 === 0 ? 1 : -1) * (2 + ((i*7) % 6));
  card.style.transform = 'rotate('+rot+'deg)';
  card.style.animationDelay = (i*0.08)+'s';
  card.innerHTML = '<div class="fun-fact-emoji">'+f.emoji+'</div><div class="fun-fact-text">'+f.text+'</div>';
  funFactsWrap.appendChild(card);
}});

// ---- PHOTO SLIDESHOW ----
const photoSrcs = {photo_srcs_js};
let photoIdx = 0;
const slidesEl = document.getElementById('photo-slides');
const dotsEl = document.getElementById('photo-dots');

photoSrcs.forEach((src, i) => {{
  const slide = document.createElement('div');
  slide.className = 'photo-slide' + (i>0?' hidden':'');
  if(src.startsWith('__placeholder_')){{
    const emoji = src.replace('__placeholder_','').replace('__','');
    slide.innerHTML = '<div class="ph">'+emoji+'</div>';
  }} else {{
    slide.innerHTML = '<img src="'+src+'" alt="pic">';
  }}
  slidesEl.appendChild(slide);

  const dot = document.createElement('div');
  dot.className = 'photo-dot'+(i===0?' active':'');
  dotsEl.appendChild(dot);
}});

function nextPhoto(){{
  const slides = slidesEl.querySelectorAll('.photo-slide');
  const dots = dotsEl.querySelectorAll('.photo-dot');
  slides[photoIdx].classList.add('hidden');
  dots[photoIdx].classList.remove('active');
  photoIdx = (photoIdx+1)%slides.length;
  slides[photoIdx].classList.remove('hidden');
  dots[photoIdx].classList.add('active');
}}

// ---- GAME ----
const questions=[
  {{q:'ur old now aren\\'t u? &#128514;', yesLabel:'yes &#128557;', noLabel:'no', win:'lessgoo u admitted itt &#128514;&#128151;'}},
  {{q:'should i be slapped? &#129767;', yesLabel:'no &#128557;', noLabel:'yes', win:'phew... no it is &#128557; saved'}},
  {{q:'ur da best bsf right? &#129402;', yesLabel:'yes ofc &#128151;', noLabel:'no', win:'lessgoo correct answer only &#128151;'}},
  {{q:'will u be more active this year? &#128247;', yesLabel:'yes i will &#128151;', noLabel:'no', win:'say less, locked in &#128151;&#128247;'}},
  {{q:'will u enjoy ur bday? &#127874;', yesLabel:'absolutely &#127874;', noLabel:'no', win:'lessgoo as it should be &#127874;&#128151;'}},
];
let qIdx=0,noEscapes=0,gameWon=false,lastFleeTime=0;
const noBtn=document.getElementById('no-btn');
const yesBtn=document.getElementById('yes-btn');
const arena=document.getElementById('game-arena');

function updateGameQuestion(){{
  document.getElementById('game-question').innerHTML=questions[qIdx].q;
  yesBtn.innerHTML=questions[qIdx].yesLabel;
  noBtn.textContent=questions[qIdx].noLabel;
  noEscapes=0;
  noBtn.style.fontSize='0.82rem';
  noBtn.style.left='70%';
  noBtn.style.top='50%';
}}

// flee AWAY from the pointer position (px, py are relative to the arena),
// instead of jumping to a random spot that might still be under the cursor.
function fleeFrom(px,py){{
  if(gameWon) return;
  const now=Date.now();
  if(now-lastFleeTime<220) return; // throttle so it doesn't jitter every pixel of movement
  lastFleeTime=now;
  noEscapes++;
  const size=Math.max(0.55,0.82-noEscapes*0.04);
  noBtn.style.fontSize=size+'rem';
  noBtn.style.transition='left 0.4s cubic-bezier(.25,.46,.45,.94),top 0.4s cubic-bezier(.25,.46,.45,.94),font-size 0.2s ease';
  const aw=arena.offsetWidth, ah=arena.offsetHeight;
  const bw=noBtn.offsetWidth, bh=noBtn.offsetHeight;
  const bx=noBtn.offsetLeft+bw/2, by=noBtn.offsetTop+bh/2;
  let dx=bx-px, dy=by-py;
  const dist=Math.hypot(dx,dy)||1;
  const ux=dx/dist, uy=dy/dist;
  let nx=bx+ux*100+(Math.random()-0.5)*30;
  let ny=by+uy*70+(Math.random()-0.5)*30;
  nx=Math.max(bw/2,Math.min(nx,aw-bw/2));
  ny=Math.max(bh/2,Math.min(ny,ah-bh/2));
  // stay clear of the yes button (left ~40% of arena)
  if(nx<aw*0.42) nx=aw*0.55+Math.random()*aw*0.35;
  noBtn.style.left=nx+'px';
  noBtn.style.top=ny+'px';
  if(noEscapes>=5) noBtn.textContent='noooo 😭';
  else if(noEscapes>=3) noBtn.textContent='no... 🫣';
}}

function arenaPointFromMouse(e){{
  const rect=arena.getBoundingClientRect();
  return [e.clientX-rect.left, e.clientY-rect.top];
}}
function arenaPointFromTouch(e){{
  const t=e.touches[0]||e.changedTouches[0];
  if(!t) return null;
  const rect=arena.getBoundingClientRect();
  return [t.clientX-rect.left, t.clientY-rect.top];
}}
function proximityCheck(px,py){{
  const bx=noBtn.offsetLeft+noBtn.offsetWidth/2, by=noBtn.offsetTop+noBtn.offsetHeight/2;
  if(Math.hypot(px-bx,py-by)<75) fleeFrom(px,py);
}}
arena.addEventListener('mousemove', e=>{{ const p=arenaPointFromMouse(e); proximityCheck(p[0],p[1]); }});
arena.addEventListener('touchstart', e=>{{ const p=arenaPointFromTouch(e); if(p) proximityCheck(p[0],p[1]); }}, {{passive:true}});
arena.addEventListener('touchmove', e=>{{ const p=arenaPointFromTouch(e); if(p) proximityCheck(p[0],p[1]); }}, {{passive:true}});

function yesClicked(){{
  if(gameWon) return;
  gameWon=true;
  yesBtn.style.display='none'; noBtn.style.display='none';
  const result=document.getElementById('game-result');
  result.style.display='block';
  result.innerHTML=questions[qIdx].win;
  heartShower();
  setTimeout(()=>{{
    qIdx=(qIdx+1)%questions.length;
    gameWon=false;
    yesBtn.style.display='block'; noBtn.style.display='block';
    result.style.display='none';
    updateGameQuestion();
  }},2500);
}}

// ---- AUDIO PLAYER ----
const audio = document.getElementById('sayu-audio');
const playBtn = document.getElementById('play-btn');
const progressFill = document.getElementById('progress-fill');
const curTime = document.getElementById('cur-time');
const durTime = document.getElementById('dur-time');
const bars = document.querySelectorAll('.audio-bar');
let isPlaying = false;

// ---- REAL AUDIO-REACTIVE BARS (Web Audio API) ----
let audioCtx=null, analyser=null, freqData=null, analyserReady=false;
function setupAnalyser() {{
  if (analyserReady) return;
  try {{
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const sourceNode = audioCtx.createMediaElementSource(audio);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 64;
    analyser.smoothingTimeConstant = 0.75;
    sourceNode.connect(analyser);
    analyser.connect(audioCtx.destination);
    freqData = new Uint8Array(analyser.frequencyBinCount);
    analyserReady = true;
  }} catch(err) {{ analyserReady = false; }}
}}
function animateBars() {{
  if (analyserReady && !audio.paused) {{
    analyser.getByteFrequencyData(freqData);
    bars.forEach((b,i) => {{
      const idx = 1 + Math.floor(i * (freqData.length-1) / bars.length);
      const v = freqData[idx] / 255;
      b.style.height = (6 + v*46) + 'px';
    }});
  }} else if (!isPlaying) {{
    bars.forEach(b => b.style.height = '6px');
  }}
  requestAnimationFrame(animateBars);
}}
requestAnimationFrame(animateBars);

function togglePlay() {{
  if (!audio.src || audio.src === window.location.href) return;
  setupAnalyser();
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
  if (isPlaying) {{
    audio.pause();
    isPlaying = false;
    playBtn.innerHTML = '&#9654;&#65039;';
  }} else {{
    audio.play();
    isPlaying = true;
    playBtn.innerHTML = '&#9646;&#9646;';
  }}
}}

function fmtTime(s) {{
  const m = Math.floor(s/60);
  const sec = Math.floor(s%60);
  return m+':'+(sec<10?'0':'')+sec;
}}

audio.addEventListener('timeupdate', () => {{
  if (audio.duration) {{
    progressFill.style.width = (audio.currentTime/audio.duration*100)+'%';
    curTime.textContent = fmtTime(audio.currentTime);
  }}
}});

audio.addEventListener('loadedmetadata', () => {{
  durTime.textContent = fmtTime(audio.duration);
}});

audio.addEventListener('ended', () => {{
  isPlaying = false;
  playBtn.innerHTML = '&#9654;&#65039;';
  progressFill.style.width = '0%';
  curTime.textContent = '0:00';
}});

function seekAudio(e) {{
  if (!audio.duration) return;
  const rect = document.getElementById('progress-wrap').getBoundingClientRect();
  const clientX = (e.changedTouches && e.changedTouches.length) ? e.changedTouches[0].clientX : e.clientX;
  const pct = (clientX - rect.left) / rect.width;
  audio.currentTime = Math.min(Math.max(pct,0),1) * audio.duration;
}}
</script>
</body>
</html>"""

components.html(html, height=750, scrolling=False)
