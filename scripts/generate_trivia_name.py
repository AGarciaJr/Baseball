import sys, os, random, json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from sqlalchemy import text

def generate_team_players_question():
    now        = datetime.now().year
    start_year = random.randint(1990, now - 1)
    end_year   = random.randint(start_year + 1, now)

    # scale number of names to the span length
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
                SELECT b.playerID FROM batting b EHERE b.teamID  = :team_id AND b.yearID BETWEEN :start_year AND :end_year
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
        # … you don’t store answers …
        question_text = (
            f"Can you name {x} players who played for the {team_name} "
            f"between {start_year} and {end_year}?"
        )

        # insert just the parameters—answers are checked at submission time
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

if __name__ == "__main__":
    generate_team_players_question()
