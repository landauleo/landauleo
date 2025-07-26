from datetime import datetime
import requests
import re

USERNAME = "landauleo"
YEAR = datetime.now().year
URL = f"https://api.github.com/users/{USERNAME}/events/public"

def get_active_days(username):
    page = 1
    active_days = set()

    while True:
        resp = requests.get(f"{URL}?page={page}", headers={"Accept": "application/vnd.github.v3+json"})
        data = resp.json()

        if not data:
            break

        for event in data:
            date = event["created_at"]
            year = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").year
            if year == YEAR:
                active_days.add(date[:10])
            elif year < YEAR:
                return len(active_days)

        page += 1

    return len(active_days)

def update_readme():
    active_days = get_active_days(USERNAME)

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_line = f"Active days in {YEAR}: **{active_days}**"
    updated_content, count = re.subn(
        r"Active days in \d{4}: \*\*\d+\*\*",
        new_line,
        content
    )

    if count == 0:
        # Если строка не найдена — добавить в конец файла
        updated_content += f"\n\n{new_line}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    update_readme()
