from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

"""
halloffame_generator.py

Generates questions about Hall of Fame:
  - Who was inducted into the Hall of Fame in [Year]?
  - In what year was [Player] inducted into the Hall of Fame?
  - Which category was [Player] inducted as?
"""

class HallOfFameTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for Hall of Fame-related questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Hall of Fame'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Hall of Fame' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_inductee_by_year_question,
            self._generate_year_of_induction_question,
            self._generate_category_of_induction_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid Hall of Fame trivia question after multiple attempts.")

    def _generate_inductee_by_year_question(self):
        query = text("""
            SELECT h.yearID, h.playerID, p.nameFirst, p.nameLast
            FROM halloffame h
            JOIN people p ON h.playerID = p.playerID
            WHERE h.inducted = 'Y'
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No Hall of Fame inductee found.")

        distractor_query = text("""
            SELECT nameFirst, nameLast
            FROM people
            WHERE playerID != :playerID
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'playerID': row.playerID}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor players found.")

        choices = [f"{row.nameFirst} {row.nameLast}"] + [f"{d.nameFirst} {d.nameLast}" for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == f"{row.nameFirst} {row.nameLast}")
        question_text = f"Who was inducted into the Hall of Fame in {row.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_year_of_induction_question(self):
        query = text("""
            SELECT h.yearID, p.nameFirst, p.nameLast
            FROM halloffame h
            JOIN people p ON h.playerID = p.playerID
            WHERE h.inducted = 'Y'
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No Hall of Fame inductee found.")

        distractor_years = set()
        while len(distractor_years) < 3:
            y = random.randint(1936, 2022)
            if y != row.yearID:
                distractor_years.add(y)
        choices = [str(row.yearID)] + [str(y) for y in distractor_years]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, year in labeled if year == str(row.yearID))
        question_text = f"In what year was {row.nameFirst} {row.nameLast} inducted into the Hall of Fame?"
        return question_text, dict(labeled), correct_letter

    def _generate_category_of_induction_question(self):
        query = text("""
            SELECT h.category, p.nameFirst, p.nameLast
            FROM halloffame h
            JOIN people p ON h.playerID = p.playerID
            WHERE h.inducted = 'Y' AND h.category IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No Hall of Fame inductee with category found.")

        distractor_query = text("""
            SELECT DISTINCT category
            FROM halloffame
            WHERE category IS NOT NULL AND category != :category
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'category': row.category}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor categories found.")

        choices = [row.category] + [d.category for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, cat in labeled if cat == row.category)
        question_text = f"Which category was {row.nameFirst} {row.nameLast} inducted as?"
        return question_text, dict(labeled), correct_letter 