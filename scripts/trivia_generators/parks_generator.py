from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

"""
parks_generator.py

Generates questions about ballparks:
    - In which city is [Park Name] located?
    - Which park is located in [City]?
    - Which state is home to [Park Name]?
"""

class ParksTriviaGenerator(BaseTriviaGenerator):
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Parks'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Parks' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_park_city_question,
            self._generate_park_by_city_question,
            self._generate_park_state_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid parks trivia question after multiple attempts.")

    def _generate_park_city_question(self):
        query = text("""
            SELECT park_name, city
            FROM parks
            WHERE city IS NOT NULL AND park_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No park with a valid city found.")

        distractor_query = text("""
            SELECT DISTINCT city
            FROM parks
            WHERE city IS NOT NULL AND city != :city
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'city': row.city}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor cities found.")

        choices = [row.city] + [d.city for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, city in labeled if city == row.city)
        question_text = f"In which city is {row.park_name} located?"
        return question_text, dict(labeled), correct_letter

    def _generate_park_by_city_question(self):
        query = text("""
            SELECT park_name, city
            FROM parks
            WHERE city IS NOT NULL AND park_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No park with a valid city found.")

        distractor_query = text("""
            SELECT DISTINCT park_name
            FROM parks
            WHERE park_name IS NOT NULL AND park_name != :park_name
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'park_name': row.park_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor parks found.")

        choices = [row.park_name] + [d.park_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, park in labeled if park == row.park_name)
        question_text = f"Which park is located in {row.city}?"
        return question_text, dict(labeled), correct_letter

    def _generate_park_state_question(self):
        query = text("""
            SELECT park_name, state
            FROM parks
            WHERE state IS NOT NULL AND park_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No park with a valid state found.")

        distractor_query = text("""
            SELECT DISTINCT state
            FROM parks
            WHERE state IS NOT NULL AND state != :state
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'state': row.state}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor states found.")

        choices = [row.state] + [d.state for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, state in labeled if state == row.state)
        question_text = f"Which state is home to {row.park_name}?"
        return question_text, dict(labeled), correct_letter 