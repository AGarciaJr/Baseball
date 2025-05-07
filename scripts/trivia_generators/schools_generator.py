from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

"""
schools_generator.py

Generates questions about schools:
  - In which city is [School Name] located?
  - In which state is [School Name] located?
  - In which country is [School Name] located?
"""

class SchoolsTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for school-related questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Schools'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Schools' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_school_city_question,
            self._generate_school_state_question,
            self._generate_school_country_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid schools trivia question after multiple attempts.")

    def _generate_school_city_question(self):
        query = text("""
            SELECT school_name, school_city
            FROM schools
            WHERE school_city IS NOT NULL AND school_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No school with a valid city found.")

        distractor_query = text("""
            SELECT DISTINCT school_city
            FROM schools
            WHERE school_city IS NOT NULL AND school_city != :school_city
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'school_city': row.school_city}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor cities found.")

        choices = [row.school_city] + [d.school_city for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, city in labeled if city == row.school_city)
        question_text = f"In which city is {row.school_name} located?"
        return question_text, dict(labeled), correct_letter

    def _generate_school_state_question(self):
        query = text("""
            SELECT school_name, school_state
            FROM schools
            WHERE school_state IS NOT NULL AND school_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No school with a valid state found.")

        distractor_query = text("""
            SELECT DISTINCT school_state
            FROM schools
            WHERE school_state IS NOT NULL AND school_state != :school_state
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'school_state': row.school_state}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor states found.")

        choices = [row.school_state] + [d.school_state for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, state in labeled if state == row.school_state)
        question_text = f"In which state is {row.school_name} located?"
        return question_text, dict(labeled), correct_letter

    def _generate_school_country_question(self):
        query = text("""
            SELECT school_name, school_country
            FROM schools
            WHERE school_country IS NOT NULL AND school_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No school with a valid country found.")

        distractor_query = text("""
            SELECT DISTINCT school_country
            FROM schools
            WHERE school_country IS NOT NULL AND school_country != :school_country
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'school_country': row.school_country}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor countries found.")

        choices = [row.school_country] + [d.school_country for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, country in labeled if country == row.school_country)
        question_text = f"In which country is {row.school_name} located?"
        return question_text, dict(labeled), correct_letter 