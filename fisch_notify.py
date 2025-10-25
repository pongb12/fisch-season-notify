import requests
from bs4 import BeautifulSoup
import datetime
import os

URL = "https://fischipedia.org/wiki/Fisch_Wiki"
WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1431501749142814740/Sc4y4biMZEB7wwegVzdm3ZH6gO0mm_fPFspU5_YPvlKS8O1wt-fAdK92mjpOpydns3bA")

def get_season_info():
    r = requests.get(URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    season_divs = soup.select(".season-cell")
    result = []

    for s in season_divs:
        # Tên mùa (spring / summer / autumn / winter)
        name = [c.replace("season-", "") for c in s["class"]
                if c.startswith("season-") and c not in ("season-cell", "current-season")]
        is_current = "current-season" in s["class"]

        cd_div = s.select_one(".season-cd")
        cd_text = cd_div.text.strip() if cd_div else "?"
        cd_content = s.select_one(".season-cd-content")
        time_text = cd_content.text.strip() if cd_content else "?"
        time_title = cd_content["title"] if cd_content and "title" in cd_content.attrs else "?"

        result.append({
            "name": name[0] if name else "?",
            "current": is_current,
            "cd_text": cd_text,
            "time_text": time_text,
            "time_title": time_title
        })
    return result

def send_to_discord(message):
    if not WEBHOOK_URL:
        print("⚠️ Missing DISCORD_WEBHOOK")
        return
    try:
        res = requests.post(WEBHOOK_URL, json={"content": message})
        res.raise_for_status()
        print("✅ Sent to Discord!")
    except Exception as e:
        print(f"❌ Error sending to Discord: {e}")

def main():
    seasons = get_season_info()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"🕒 **Cập nhật mùa Fisch Game** ({now})\n"
    msg += "---------------------------------\n"

    for s in seasons:
        icon = {
            "summer": "☀️",
            "autumn": "🍂",
            "winter": "❄️",
            "spring": "🌱"
        }.get(s["name"], "❔")

        status = "🔸 **Hiện tại**" if s["current"] else "Sắp tới"
        msg += f"{icon} **{s['name'].capitalize()}** - {status}\n"
        msg += f"⏳ {s['cd_text']} `{s['time_text']}` ({s['time_title']})\n\n"

    send_to_discord(msg)

if __name__ == "__main__":
    main()
