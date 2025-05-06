from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class FranchisesTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for franchise-related questions.

    Generates questions about franchises:
      - What is the full name of the franchise with ID [franchID]?
      - Which franchise is currently active?
      - Which franchise is associated with the NAassoc code [NAassoc]?
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Franchises'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Franchises' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_full_name_question,
            self._generate_active_franchise_question,
            self._generate_naassoc_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid franchises trivia question after multiple attempts.")

    def _generate_full_name_question(self):
        query = text("""
            SELECT franchID, franchName
            FROM franchises
            WHERE franchName IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No franchise with a valid name found.")

        distractor_query = text("""
            SELECT franchName
            FROM franchises
            WHERE franchName IS NOT NULL AND franchName != :franchName
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'franchName': row.franchName}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor franchise names found.")

        choices = [row.franchName] + [d.franchName for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.franchName)
        question_text = f"What is the full name of the franchise with ID {row.franchID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_active_franchise_question(self):
        query = text("""
            SELECT franchName
            FROM franchises
            WHERE active = 'Y'
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No active franchise found.")

        distractor_query = text("""
            SELECT franchName
            FROM franchises
            WHERE active != 'Y' AND franchName != :franchName
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'franchName': row.franchName}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor franchise names found.")

        choices = [row.franchName] + [d.franchName for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.franchName)
        question_text = f"Which franchise is currently active?"
        return question_text, dict(labeled), correct_letter

    def _generate_naassoc_question(self):
        query = text("""
            SELECT franchName, NAassoc
            FROM franchises
            WHERE NAassoc IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No franchise with a valid NAassoc found.")

        distractor_query = text("""
            SELECT franchName
            FROM franchises
            WHERE franchName != :franchName
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'franchName': row.franchName}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor franchise names found.")

        choices = [row.franchName] + [d.franchName for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == row.franchName)
        question_text = f"Which franchise is associated with the NAassoc code {row.NAassoc}?"
        return question_text, dict(labeled), correct_letter 