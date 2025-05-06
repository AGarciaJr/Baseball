from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class SeriesPostTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for postseason series questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Postseason'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Postseason' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_series_winner_question,
            self._generate_series_loser_question,
            self._generate_series_round_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid seriespost trivia question after multiple attempts.")

    def _generate_series_winner_question(self):
        query = text("""
            SELECT yearID, round, teamIDwinner
            FROM seriespost
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No series winner found.")

        distractor_query = text("""
            SELECT DISTINCT teamIDwinner
            FROM seriespost
            WHERE teamIDwinner != :teamIDwinner
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'teamIDwinner': row.teamIDwinner}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor teams found.")

        choices = [row.teamIDwinner] + [d.teamIDwinner for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, team in labeled if team == row.teamIDwinner)
        question_text = f"Which team won the {row.round} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_series_loser_question(self):
        query = text("""
            SELECT yearID, round, teamIDloser
            FROM seriespost
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No series loser found.")

        distractor_query = text("""
            SELECT DISTINCT teamIDloser
            FROM seriespost
            WHERE teamIDloser != :teamIDloser
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'teamIDloser': row.teamIDloser}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor teams found.")

        choices = [row.teamIDloser] + [d.teamIDloser for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, team in labeled if team == row.teamIDloser)
        question_text = f"Which team lost the {row.round} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_series_round_question(self):
        query = text("""
            SELECT yearID, round
            FROM seriespost
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No series round found.")

        distractor_query = text("""
            SELECT DISTINCT round
            FROM seriespost
            WHERE round != :round
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'round': row.round}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor rounds found.")

        choices = [row.round] + [d.round for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, rnd in labeled if rnd == row.round)
        question_text = f"Which round was played in {row.yearID}?"
        return question_text, dict(labeled), correct_letter 