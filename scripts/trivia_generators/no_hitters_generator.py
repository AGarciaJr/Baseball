"""
no_hitters_generator.py

Generates questions about no-hitters:
  - Which team threw a no-hitter on [Date]?
  - Which team was no-hit on [Date]?
  - In what year did the [Team] throw a no-hitter on [Date]?
"""

from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class NoHittersTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for no-hitter questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'No-Hitters'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'No-Hitters' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_no_hitter_team_question,
            self._generate_no_hitter_opponent_question,
            self._generate_no_hitter_year_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid no_hitters trivia question after multiple attempts.")

    def _generate_no_hitter_team_question(self):
        query = text("""
            SELECT nh.game_date, t.team_name
            FROM no_hitters nh
            JOIN teams t ON nh.team_id = t.teams_ID
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No no-hitter found.")

        distractor_query = text("""
            SELECT DISTINCT team_name
            FROM teams
            WHERE team_name != :team_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'team_name': row.team_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor teams found.")

        choices = [row.team_name] + [d.team_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.team_name)
        question_text = f"Which team threw a no-hitter on {row.game_date}?"
        return question_text, dict(labeled), correct_letter

    def _generate_no_hitter_opponent_question(self):
        query = text("""
            SELECT nh.game_date, t.team_name AS opponent
            FROM no_hitters nh
            JOIN teams t ON nh.opponent_id = t.teams_ID
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No no-hitter opponent found.")

        distractor_query = text("""
            SELECT DISTINCT team_name
            FROM teams
            WHERE team_name != :team_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'team_name': row.opponent}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor teams found.")

        choices = [row.opponent] + [d.team_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.opponent)
        question_text = f"Which team was no-hit on {row.game_date}?"
        return question_text, dict(labeled), correct_letter

    def _generate_no_hitter_year_question(self):
        query = text("""
            SELECT nh.game_date, t.team_name
            FROM no_hitters nh
            JOIN teams t ON nh.team_id = t.teams_ID
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row or not row.game_date:
            raise Exception("No no-hitter with a valid date found.")

        year = row.game_date.year
        distractor_years = set()
        while len(distractor_years) < 3:
            y = random.randint(1876, 2022)
            if y != year:
                distractor_years.add(y)
        choices = [str(year)] + [str(y) for y in distractor_years]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, y in labeled if y == str(year))
        question_text = f"In what year did the {row.team_name} throw a no-hitter on {row.game_date}?"
        return question_text, dict(labeled), correct_letter 