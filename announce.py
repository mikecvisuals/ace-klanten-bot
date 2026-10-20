"""
Ace Creative Agency – klanten-aankondiger

Kijkt of er een nieuwe post in het forum 📋-klanten staat en zet die
automatisch in #aankondigingen, met een tag voor de Editor-rol.

Draait als korte taak (bijv. elke 30 minuten via GitHub Actions).
Er is geen database nodig: het script kijkt in #aankondigingen welke
klanten de bot al heeft aangekondigd en slaat die over.

Instellingen (omgevingsvariabelen):
  DISCORD_TOKEN         Bot-token uit de Discord Developer Portal (geheim!)
  GUILD_ID              ID van de server
  FORUM_CHANNEL_ID      ID van 📋-klanten
  ANNOUNCE_CHANNEL_ID   ID van #aankondigingen
  EDITOR_ROLE_ID        ID van de rol Editor (optioneel, voor de melding)
  MAX_AGE_HOURS         Alleen posts nieuwer dan dit aankondigen (standaard 24)

Testen zonder iets te plaatsen:  python announce.py --dry-run
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://discord.com/api/v10"
DISCORD_EPOCH_MS = 1420070400000
EMBED_COLOR = 0x5865F2


# ---------- Discord API ----------

def api(method, path, body=None):
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", "Bot " + os.environ["DISCORD_TOKEN"])
        req.add_header("User-Agent", "AceKlantenBot (https://acecreativeagency.nl, 1.0)")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limit: even wachten en opnieuw
                wait = float(json.loads(e.read() or b"{}").get("retry_after", 2))
                time.sleep(wait + 0.5)
                continue
            detail = e.read().decode(errors="replace")
            raise SystemExit(f"Discord gaf fout {e.code} op {method} {path}: {detail}")
    raise SystemExit(f"Te vaak een rate limit op {path}, probeer het later opnieuw.")


# ---------- Hulpfuncties ----------

def snowflake_ms(snowflake):
    return (int(snowflake) >> 22) + DISCORD_EPOCH_MS


def clean_title(name):
    # Haal de 🎬 en spaties aan het begin weg
    return re.sub(r"^[^\w]+", "", name).strip() or name


def already_announced(announce_channel_id, bot_id):
    """Thread-ID's die de bot al eerder in #aankondigingen heeft gezet."""
    done = set()
    messages = api("GET", f"/channels/{announce_channel_id}/messages?limit=100") or []
    for msg in messages:
        if msg.get("author", {}).get("id") != bot_id:
            continue
        for embed in msg.get("embeds", []):
            m = re.search(r"/channels/\d+/(\d+)", embed.get("url", ""))
            if m:
                done.add(m.group(1))
    return done


def build_message(guild_id, thread, starter_text, tag_names, editor_role_id):
    name = clean_title(thread["name"])
    link = f"https://discord.com/channels/{guild_id}/{thread['id']}"
    description = (starter_text or "").strip()
    if len(description) > 3500:
        description = description[:3500].rstrip() + "…"
    description += f"\n\n👉 [Bekijk de volledige info]({link})"

    embed = {
        "title": f"🆕 Nieuwe klant: {name}",
        "url": link,
        "description": description,
        "color": EMBED_COLOR,
        "footer": {"text": "Alle klanten vind je in 📋-klanten"},
    }
    if tag_names:
        embed["fields"] = [{"name": "Status", "value": " · ".join(tag_names), "inline": False}]

    content = f"Er is een nieuwe klant bij! Check even wat we voor **{name}** gaan doen."
    allowed = {"parse": []}
    if editor_role_id:
        content = f"<@&{editor_role_id}> " + content
        allowed = {"roles": [editor_role_id]}

    return {"content": content, "embeds": [embed], "allowed_mentions": allowed}


# ---------- Hoofdprogramma ----------

def main():
    dry_run = "--dry-run" in sys.argv
    guild_id = os.environ["GUILD_ID"]
    forum_id = os.environ["FORUM_CHANNEL_ID"]
    announce_id = os.environ["ANNOUNCE_CHANNEL_ID"]
    editor_role_id = os.environ.get("EDITOR_ROLE_ID", "").strip()
    max_age_ms = float(os.environ.get("MAX_AGE_HOURS", "24")) * 3600 * 1000

    bot = api("GET", "/users/@me")
    forum = api("GET", f"/channels/{forum_id}")
    tag_lookup = {t["id"]: t["name"] for t in forum.get("available_tags", [])}

    active = api("GET", f"/guilds/{guild_id}/threads/active") or {}
    posts = [t for t in active.get("threads", []) if t.get("parent_id") == forum_id]

    now_ms = time.time() * 1000
    new_posts = [t for t in posts if now_ms - snowflake_ms(t["id"]) <= max_age_ms]
    new_posts.sort(key=lambda t: int(t["id"]))  # oudste eerst

    if not new_posts:
        print("Geen nieuwe klantposts gevonden.")
        return

    done = already_announced(announce_id, bot["id"])
    todo = [t for t in new_posts if t["id"] not in done]
    if not todo:
        print("Nieuwe posts zijn al aangekondigd.")
        return

    for thread in todo:
        # Bij een forumpost heeft het eerste bericht hetzelfde ID als de post zelf
        starter = api("GET", f"/channels/{thread['id']}/messages/{thread['id']}") or {}
        tags = [tag_lookup[t] for t in thread.get("applied_tags", []) if t in tag_lookup]
        payload = build_message(guild_id, thread, starter.get("content", ""), tags, editor_role_id)

        if dry_run:
            print("[TEST] zou dit plaatsen:\n" + json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            api("POST", f"/channels/{announce_id}/messages", payload)
            print(f"Aangekondigd: {thread['name']}")


if __name__ == "__main__":
    main()
