from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random

class PitchingTriviaGenerator(BaseTriviaGenerator):
    def __init__(self):
        # Get the category ID for pitching
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Pitching'")
            ).fetchone()
            super().__init__(result.id)

    def generate_question(self):
        question_types = [
            self._generate_strikeout_question,
            self._generate_era_question,
            self._generate_wins_question
        ]
        
        # Randomly select a question type
        generator = random.choice(question_types)
        return generator()

    def _generate_strikeout_question(self):
        year = random.randint(1980, 2022)
        
        query = text("""
            SELECT p.nameFirst, p.nameLast, pitching.p_SO
            FROM pitching
            JOIN people p ON p.playerID = pitching.playerID
            WHERE pitching.yearID = :year
            AND pitching.p_SO IS NOT NULL
            ORDER BY pitching.p_SO DESC
            LIMIT 4
        """)

        result = db.session.execute(query, {'year': year})
        players = result.fetchall()

        if len(players) < 4:
            raise Exception(f"Not enough data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]

        # Shuffle choices
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)

        question_text = f"Who had the most strikeouts in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_era_question(self):
        year = random.randint(1980, 2022)
        
        query = text("""
            SELECT p.nameFirst, p.nameLast, pitching.p_ERA
            FROM pitching
            JOIN people p ON p.playerID = pitching.playerID
            WHERE pitching.yearID = :year
            AND pitching.p_ERA IS NOT NULL
            AND pitching.p_IPOuts >= 162  -- Minimum 54 innings pitched
            ORDER BY pitching.p_ERA ASC
            LIMIT 4
        """)

        result = db.session.execute(query, {'year': year})
        players = result.fetchall()

        if len(players) < 4:
            raise Exception(f"Not enough data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]

        # Shuffle choices
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)

        question_text = f"Who had the lowest ERA in {year} (minimum 54 innings pitched)?"
        return question_text, dict(labeled), correct_letter

    def _generate_wins_question(self):
        year = random.randint(1980, 2022)
        
        query = text("""
            SELECT p.nameFirst, p.nameLast, pitching.p_W
            FROM pitching
            JOIN people p ON p.playerID = pitching.playerID
            WHERE pitching.yearID = :year
            AND pitching.p_W IS NOT NULL
            ORDER BY pitching.p_W DESC
            LIMIT 4
        """)

        result = db.session.execute(query, {'year': year})
        players = result.fetchall()

        if len(players) < 4:
            raise Exception(f"Not enough data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]

        # Shuffle choices
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)

        question_text = f"Who had the most wins in {year}?"
        return question_text, dict(labeled), correct_letter 