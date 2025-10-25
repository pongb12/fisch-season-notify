import os
import requests
from bs4 import BeautifulSoup

URL = "https://fischipedia.org/wiki/Fisch_Wiki"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

def get_seasons():
    """Trích xuất thông tin mùa từ trang fischipedia.org"""
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    result = []
    season_divs = soup.select("div.countdown.countdown-seasons > div.season-cell")

    for div in season_divs:
        name_class = div.get("class", [])
        season_name = next((c.replace("season-", "") for c in name_class if c.startswith("season-") and c != "season-cell"), "unknown")
        current = "current-season" in name_class

        time_span = div.select_one(".season-cd-content")
        if time_span:
            title = time_span.get("title", "")
            countdown = time_span.text.strip()
        else:
            title, countdown = "N/A", "N/A"

        result.append({
            "name": season_name.capitalize(),
            "current": current,
            "title": title,
            "countdown": countdown
        })
    return result


def send_to_discord(data):
    """Gửi thông tin mùa đến Discord webhook"""
    if not WEBHOOK_URL:
        print("⚠️ Missing DISCORD_WEBHOOK environment variable")
        return

    current = next((s for s in data if s["current"]), None)
    upcoming = next((s for s in data if not s["current"]), None)

    embed = {
        "title": "🌦️Seasons Update",
        "color": 0x00FFAA,
        "fields": []
    }

    for s in data:
        icon = "☀️" if s["name"] == "Summer" else "🍂" if s["name"] == "Autumn" else "❄️" if s["name"] == "Winter" else "🌱"
        embed["fields"].append({
            "name": f"{icon} {s['name']}" + (" (Current)" if s["current"] else ""),
            "value": f"**Time:** {s['title']}\n**Countdown:** {s['countdown']}",
            "inline": False
        })

    payload = {"embeds": [embed]}
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("✅ Sent to Discord successfully!")
    else:
        print(f"❌ Failed to send ({response.status_code}): {response.text}")


if __name__ == "__main__":
    print("🔍 Fetching season data...")
    seasons = get_seasons()
    for s in seasons:
        print(f"- {s['name']}: {s['countdown']} (current={s['current']})")

    print("📤 Sending to Discord...")
    send_to_discord(seasons)
