from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class DivisionsTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for division-related questions.

    Generates questions about divisions:
      - What is the full name of the division with ID [divID]?
      - Which league is the [Division Name] division part of?
      - In what year did the [Division Name] division begin play?
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Divisions'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Divisions' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_division_name_question,
            self._generate_division_league_question,
            self._generate_first_year_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid divisions trivia question after multiple attempts.")

    def _generate_division_name_question(self):
        query = text("""
            SELECT divID, division_name
            FROM divisions
            WHERE division_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No division with a valid name found.")

        distractor_query = text("""
            SELECT division_name
            FROM divisions
            WHERE division_name IS NOT NULL AND division_name != :division_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'division_name': row.division_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor division names found.")

        choices = [row.division_name] + [d.division_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.division_name)
        question_text = f"What is the full name of the division with ID {row.divID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_division_league_question(self):
        query = text("""
            SELECT division_name, lgID
            FROM divisions
            WHERE division_name IS NOT NULL AND lgID IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No division with a valid league found.")

        distractor_query = text("""
            SELECT DISTINCT lgID
            FROM divisions
            WHERE lgID IS NOT NULL AND lgID != :lgID
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'lgID': row.lgID}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor leagues found.")

        choices = [row.lgID] + [d.lgID for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, lg in labeled if lg == row.lgID)
        question_text = f"Which league is the {row.division_name} division part of?"
        return question_text, dict(labeled), correct_letter

    def _generate_first_year_question(self):
        query = text("""
            SELECT division_name, first_year
            FROM divisions
            WHERE division_name IS NOT NULL AND first_year IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No division with a valid first year found.")

        distractor_years = set()
        while len(distractor_years) < 3:
            y = random.randint(1969, 2022)
            if y != row.first_year:
                distractor_years.add(y)
        choices = [str(row.first_year)] + [str(y) for y in distractor_years]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, year in labeled if year == str(row.first_year))
        question_text = f"In what year did the {row.division_name} division begin play?"
        return question_text, dict(labeled), correct_letter 