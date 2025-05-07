"""
pitching_generator.py

Generates questions about pitching stats:
  - Who had the most strikeouts in [Year]?
  - Who had the lowest ERA in [Year] (minimum 54 innings pitched)?
  - Who had the most wins in [Year]?
"""

from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class PitchingTriviaGenerator(BaseTriviaGenerator):
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Pitching'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Pitching' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)
            self.year_min, self.year_max = self._get_year_range()

    def _get_year_range(self):
        result = db.session.execute(
            text("SELECT MIN(yearID), MAX(yearID) FROM pitching")
        ).fetchone()
        return result[0], result[1]

    def generate_question(self):
        """
        Randomly select a pitching question type and generate a question.
        """
        question_types = [
            self._generate_strikeout_question,
            self._generate_era_question,
            self._generate_wins_question
        ]
        for _ in range(10):  # Try up to 10 times to get a valid question
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid pitching trivia question after multiple attempts.")

    def _generate_strikeout_question(self):
        year = random.randint(self.year_min, self.year_max)
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
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Who had the most strikeouts in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_era_question(self):
        year = random.randint(self.year_min, self.year_max)
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

        choices = [f"{p.nameFirst} {p.nameLast} ({p.p_ERA:.2f})" for p in players]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Who had the lowest ERA in {year} (minimum 54 innings pitched)?"
        return question_text, dict(labeled), correct_letter

    def _generate_wins_question(self):
        year = random.randint(self.year_min, self.year_max)
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
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Who had the most wins in {year}?"
        return question_text, dict(labeled), correct_letter 