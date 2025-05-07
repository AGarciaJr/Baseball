import sys, os, random, json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from sqlalchemy import text

def generate_team_players_question():
    now        = datetime.now().year
    start_year = random.randint(1990, now - 1)
    end_year   = random.randint(start_year + 1, now)

    max_span = now - 1990 + 1
    span = end_year - start_year + 1
    scaled = int(span / max_span * 29)
    x = max(3, min(scaled, 10))

    with app.app_context():
        teams = db.session.execute(text("SELECT teamID, team_name FROM teams")).fetchall()
        if not teams:
            print("No teams found in the database.")
            return
        team_id, team_name = random.choice(teams)

        qry = text("""
            SELECT DISTINCT p.playerID, p.nameFirst, p.nameLast FROM (
                SELECT f.playerID FROM fielding f WHERE f.teamID = :team_id AND f.yearID BETWEEN :start_year AND :end_year
                UNION
                SELECT b.playerID FROM batting b WHERE b.teamID  = :team_id AND b.yearID BETWEEN :start_year AND :end_year
            ) AS pl
            JOIN people p ON p.playerID = pl.playerID;
        """)
        players = db.session.execute(qry, {
            'team_id':    team_id,
            'start_year':         start_year,
            'end_year':         end_year
        }).fetchall()

        if len(players) < x:
            print(f"❌ Only found {len(players)} players, need {x}.")
            return

        sampled = random.sample(players, x)
        question_text = (
            f"Can you name {x} players who played for the {team_name} "
            f"between {start_year} and {end_year}?"
        )

        ins = text("""
          INSERT INTO trivia_name_questions
            (question_text, num_required, team_id, start_year, end_year)
          VALUES
            (:q, :num, :team, :sy, :ey)
        """)
        db.session.execute(ins, {
            'q':    question_text,
            'num':  x,
            'team': team_id,
            'sy':   start_year,
            'ey':   end_year
        })
        db.session.commit()
        print(f"✅ Inserted: {question_text}")

def generate_country_players_question():
    with app.app_context():
        used = {
            row.country
            for row in db.session.execute(
                text("SELECT DISTINCT country FROM trivia_country_questions")
            ).fetchall()
        }

        country_rows = db.session.execute(text("""
            SELECT birthCountry AS country, COUNT(*) AS cnt
              FROM people
             WHERE birthCountry NOT IN :used
          GROUP BY birthCountry
            HAVING cnt >= 3
        """), {'used': tuple(used) or ('',)}).fetchall()

        if not country_rows:
            print("❌ No new countries left to seed.")
            return

        max_count = max(r.cnt for r in country_rows)

        country, count = random.choice(country_rows)

        scaled = int((count / max_count) * 20)
        x = max(3, min(scaled, 20))

        players = db.session.execute(text("""
            SELECT playerID, nameFirst, nameLast
              FROM people
             WHERE birthCountry = :country
        """), {'country': country}).fetchall()

        if len(players) < x:
            print(f"❌ Only {len(players)} players from {country}, need {x}.")
            return

        question_text = f"Can you name {x} players from {country}?"
        db.session.execute(text("""
            INSERT INTO trivia_country_questions
              (question_text, num_required, country)
            VALUES
              (:q, :num, :country)
        """), {
            'q':       question_text,
            'num':     x,
            'country': country
        })
        db.session.commit()

        print(f"✅ Inserted: {question_text}")
