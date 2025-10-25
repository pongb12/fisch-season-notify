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
        name = [c.replace("season-", "") for c in s["class"] if c.startswith("season-") and c != "season-cell"]
        is_current = "current-season" in s["class"]
        time_tag = s.select_one(".season-cd-content")
        time_text = time_tag.text.strip() if time_tag else "?"
        time_title = time_tag["title"] if time_tag else "?"
        result.append({
            "name": name[0] if name else "?",
            "current": is_current,
            "countdown": time_text,
            "title": time_title
        })
    return result

def send_to_discord(message):
    if not WEBHOOK_URL:
        print("⚠️ Missing DISCORD_WEBHOOK")
        return
    requests.post(WEBHOOK_URL, json={"content": message})

def main():
    seasons = get_season_info()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"🕒 Cập nhật mùa Fisch Game ({now})\n"
    for s in seasons:
        icon = "☀️" if s["name"]=="summer" else "🍂" if s["name"]=="autumn" else "❄️" if s["name"]=="winter" else "🌱"
        status = "🔸Hiện tại" if s["current"] else "sắp tới"
        msg += f"{icon} **{s['name'].capitalize()}** - {status}\n⏳ {s['countdown']} ({s['title']})\n"
    send_to_discord(msg)
    print("✅ Sent!")

if __name__ == "__main__":
    main()
