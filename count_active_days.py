import requests
import os
import re
from datetime import datetime

USERNAME = "landauleo"
YEAR = datetime.now().year
TOKEN = os.environ.get("GH_TOKEN")

def get_active_days_via_graphql(username):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    from_date = f"{YEAR}-01-01T00:00:00Z"
    to_date = f"{YEAR}-12-31T23:59:59Z"

    variables = {
        "username": username,
        "from": from_date,
        "to": to_date
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    data = response.json()

    if "errors" in data:
        raise Exception(f"GraphQL error: {data['errors']}")

    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    active_days = sum(
        1 for week in weeks
        for day in week['contributionDays']
        if day['contributionCount'] > 0
    )
    return active_days

def update_readme():
    active_days = get_active_days_via_graphql(USERNAME)

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
