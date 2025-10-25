
import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def main():
 
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK environment variable not set.")
        return


    url = 'https://fischipedia.org/'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching Fisch Wiki: {e}")
        return


    soup = BeautifulSoup(response.text, 'html.parser')
    seasons = {}
    for img in soup.find_all('img', alt=lambda x: x and 'season' in x):
        parent = img.parent
        if not parent:
            continue
        text = parent.get_text(separator=' ', strip=True)

        match_current = re.match(r'(\w+)\(Current\)\.\s*Next Occurrence:\s*(.*)', text)
        if match_current:
            season_name = match_current.group(1)
            next_occ = match_current.group(2)
            seasons[season_name] = {'current': True, 'next': next_occ}
        else:
            match = re.match(r'(\w+)\.\s*Next Occurrence:\s*(.*)', text)
            if match:
                season_name = match.group(1)
                next_occ = match.group(2)
                seasons[season_name] = {'current': False, 'next': next_occ}

    if not seasons:
        print("No season data found on Fisch Wiki.")
        return


    fields = []
    order = ["Spring", "Summer", "Autumn", "Winter"]
    for season in order:
        if season in seasons:
            info = seasons[season]
            name = f"{season} (Current Season)" if info['current'] else season
            value = f"Next Occurrence: {info['next']}"
            fields.append({"name": name, "value": value, "inline": False})

    embed = {
        "title": "Season Update",
        "color": 3447003,
        "fields": fields,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "footer": {"text": "Data from Fisch Wiki"}
    }
    payload = {"embeds": [embed]}


    try:
        res = requests.post(webhook_url, json=payload)
        res.raise_for_status()
    except Exception as e:
        print(f"Error sending webhook: {e}")

if __name__ == "__main__":
    main()
