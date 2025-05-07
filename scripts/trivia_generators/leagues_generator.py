from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class LeaguesTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for league-related questions.

    Generates questions about leagues:
      - What is the full name of the league with ID [lgID]?
      - Which league is currently active?
      - Which league has the code [lgID]?
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Leagues'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Leagues' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_league_name_question,
            self._generate_league_active_question,
            self._generate_league_code_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid leagues trivia question after multiple attempts.")

    def _generate_league_name_question(self):
        query = text("""
            SELECT lgID, league_name
            FROM leagues
            WHERE league_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No league with a valid name found.")

        distractor_query = text("""
            SELECT league_name
            FROM leagues
            WHERE league_name IS NOT NULL AND league_name != :league_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'league_name': row.league_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor league names found.")

        choices = [row.league_name] + [d.league_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.league_name)
        question_text = f"What is the full name of the league with ID {row.lgID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_league_active_question(self):
        query = text("""
            SELECT league_name
            FROM leagues
            WHERE league_active = 'Y'
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No active league found.")

        distractor_query = text("""
            SELECT league_name
            FROM leagues
            WHERE league_active != 'Y' AND league_name != :league_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'league_name': row.league_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor league names found.")

        choices = [row.league_name] + [d.league_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.league_name)
        question_text = f"Which league is currently active?"
        return question_text, dict(labeled), correct_letter

    def _generate_league_code_question(self):
        query = text("""
            SELECT lgID, league_name
            FROM leagues
            WHERE lgID IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No league with a valid code found.")

        distractor_query = text("""
            SELECT league_name
            FROM leagues
            WHERE league_name != :league_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'league_name': row.league_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor league names found.")

        choices = [row.league_name] + [d.league_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.league_name)
        question_text = f"Which league has the code {row.lgID}?"
        return question_text, dict(labeled), correct_letter 