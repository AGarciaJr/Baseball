import mysql.connector
import re
from datetime import datetime

# === Settings ===
host = 'localhost'
user = 'root'
password = '1111'
database = 'Sandlot2TheSQL'
input_file = 'cleaned_nohitters.txt'
pitcher_map_file = 'pitcher_playerid_map.txt'

team_aliases = {
    "Angels": "Angels",
    "Dodgers": "Dodgers",
    "Padres (in Monterrey": "Padres",
    "Twins": "Twins",
    "Indians": "Indians",
    "Mariners": "Mariners",
    "Rays": "Rays",
}

# === Load pitcher name to playerID map ===
name_to_playerid = {}
with open(pitcher_map_file, 'r') as f:
    for line in f:
        if line.strip():
            name, pid = line.strip().split('\t')
            name_to_playerid[name] = pid

# === Connect to DB ===
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    charset='utf8mb4',
    collation='utf8mb4_general_ci'
)
cursor = conn.cursor()

# === Read file ===
with open(input_file, 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

months = {
    'Jan.': '01', 'Feb.': '02', 'Mar.': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'Aug.': '08',
    'Sept.': '09', 'Oct.': '10', 'Nov.': '11', 'Dec.': '12'
}

def parse_date(raw_date):
    for k, v in months.items():
        raw_date = raw_date.replace(k, v)
    try:
        return datetime.strptime(raw_date.strip(), "%m %d, %Y").strftime("%Y-%m-%d")
    except:
        return None

def get_team_id(name_fragment, year):
    resolved = team_aliases.get(name_fragment, name_fragment)
    cursor.execute("""
        SELECT teams_ID FROM teams
        WHERE team_name LIKE %s AND yearID = %s
    """, ('%' + resolved + '%', year))
    rows = cursor.fetchall()
    return rows[0][0] if rows else None

inserted = 0
skipped = 0

for i in range(0, len(lines), 2):
    pitcher_line = lines[i]
    game_line = lines[i + 1]

    # Extract date
    date_match = re.search(r'([A-Za-z.]+ \d{1,2}, \d{4})', pitcher_line)
    if not date_match:
        print(f"[SKIP] No date in line: {pitcher_line}")
        skipped += 1
        continue
    raw_date = date_match.group(1)
    game_date = parse_date(raw_date)
    if not game_date:
        print(f"[SKIP] Unparseable date: {raw_date}")
        skipped += 1
        continue
    year = int(game_date[:4])

    # Clean pitcher names (strip innings like (2 2/3) etc.)
    pitcher_part = pitcher_line.split(raw_date)[0].strip().rstrip(',')
    pitcher_names = []
    for raw_name in pitcher_part.replace(' and ', ',').split(','):
        clean = re.sub(r'\s*\(.*?\)', '', raw_name.strip())
        if clean and not clean.isdigit():
            pitcher_names.append(clean)

    # Match team names
    team_match = re.match(r'(.+?)\s+(?:vs\.?|at)\s+(.+?)(?:,|$)', game_line)
    if not team_match:
        print(f"[SKIP] Bad team line: {game_line}")
        skipped += 1
        continue
    team_name = team_match.group(1).strip()
    opponent_name = re.sub(r'\s*\(.*?\)', '', team_match.group(2)).strip()

    team_id = get_team_id(team_name, year)
    if not team_id:
        print(f"[SKIP] Missing team ID: '{team_name}' in year {year}")
        skipped += 1
        continue

    # Lookup existing no_hitter
    cursor.execute("""
        SELECT id FROM no_hitters
        WHERE game_date = %s AND team_id = %s
    """, (game_date, team_id))
    result = cursor.fetchone()
    if not result:
        print(f"[SKIP] Could not find no_hitter entry for {game_date}, team '{team_name}'")
        skipped += 1
        continue

    no_hitter_id = result[0]

    for order, pitcher in enumerate(pitcher_names):
        player_id = name_to_playerid.get(pitcher)
        if not player_id:
            print(f"[SKIP] Missing playerID for pitcher: {pitcher}")
            continue
        cursor.execute("""
            INSERT IGNORE INTO no_hitter_pitchers (no_hitter_id, player_id, order_num)
            VALUES (%s, %s, %s)
        """, (no_hitter_id, player_id, order + 1))

    inserted += 1

conn.commit()
cursor.close()
conn.close()
print(f"✅ Linked pitchers for {inserted} no-hitter games.")
print(f"⚠️ Skipped {skipped} entries.")
