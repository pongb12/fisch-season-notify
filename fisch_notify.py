import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

URL = "https://fischipedia.org/wiki/Fisch_Wiki"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

def get_seasons():
    """Lấy thông tin 4 mùa từ trang Fischipedia"""
    print("🔍 Fetching data from website...")
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching site: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    season_divs = soup.select("div.countdown.countdown-seasons > div.season-cell")
    if not season_divs:
        print("⚠️ No season data found — check selector or site structure.")
        return []

    seasons = []
    for div in season_divs:
        classes = div.get("class", [])
        # Xác định tên mùa
        season_name = next(
            (cls.replace("season-", "") for cls in classes if cls.startswith("season-") and cls != "season-cell"),
            "unknown"
        ).capitalize()
        current = "current-season" in classes

        cd_elem = div.select_one(".season-cd-content")
        countdown = cd_elem.text.strip() if cd_elem else "N/A"
        title = cd_elem.get("title", "N/A") if cd_elem else "N/A"

        seasons.append({
            "name": season_name,
            "current": current,
            "countdown": countdown,
            "title": title
        })
    return seasons


def build_message(seasons):
    """Tạo nội dung gửi lên Discord"""
    if not seasons:
        return "⚠️ No season data available."

    now = datetime.now(timezone(timedelta(hours=7)))  # GMT+7 cho giờ Việt Nam
    msg = f"🕒 Fisch Seasons ({now.strftime('%Y-%m-%d %H:%M:%S')})\n"

    emoji_map = {
        "Summer": "☀️",
        "Autumn": "🍂",
        "Winter": "❄️",
        "Spring": "🌸",
        "Unknown": "❔"
    }

    for s in seasons:
        emoji = emoji_map.get(s["name"], "❔")
        line = f"{emoji} "
        if s["current"]:
            line += f"**Current:** {s['name']} (Ends in {s['countdown']})"
        else:
            line += f"{s['name']} (Starts in {s['countdown']})"
        msg += line + "\n"

    return msg.strip()


def send_to_discord(message):
    """Gửi tin nhắn đến Discord Webhook"""
    if not WEBHOOK_URL:
        print("⚠️ Missing DISCORD_WEBHOOK environment variable")
        return

    payload = {"content": message}
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        if res.status_code == 204:
            print("✅ Message sent to Discord successfully!")
        else:
            print(f"❌ Discord error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")


if __name__ == "__main__":
    seasons = get_seasons()
    message = build_message(seasons)
    print("\n📦 Message Preview:\n" + message)
    send_to_discord(message)
