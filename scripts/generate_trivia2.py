import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text
import random


def generate_home_run_question(year=None):
    if year is None:
        year = random.randint(1980, 2022)

    with app.app_context():
        query = text("""
            SELECT p.nameFirst, p.nameLast, b.b_HR
            FROM batting b
            JOIN people p ON p.playerID = b.playerID
            WHERE b.yearID = :year
            AND b.b_HR IS NOT NULL
            ORDER BY b.b_HR DESC
            LIMIT 4
        """)


        result = db.session.execute(query, {'year': year})
        players = result.fetchall()

        if len(players) < 4:
            print(f"Not enough data for year {year}")
            return

        # Format names
        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]

        # Shuffle choices
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)

        question_text = f"Who hit the most home runs in {year}?"

        insert_query = text("""
            INSERT INTO trivia_questions (
                question_text, choice_a, choice_b, choice_c, choice_d, correct_answer
            ) VALUES (
                :q, :a, :b, :c, :d, :correct
            )
        """)

        db.session.execute(insert_query, {
            'q': question_text,
            'a': dict(labeled)['A'],
            'b': dict(labeled)['B'],
            'c': dict(labeled)['C'],
            'd': dict(labeled)['D'],
            'correct': correct_letter
        })

        db.session.commit()
        print(f"✅ Inserted: {question_text}")

# Example run
if __name__ == "__main__":
    generate_home_run_question()
