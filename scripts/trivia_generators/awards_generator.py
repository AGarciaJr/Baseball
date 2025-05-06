from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

"""
awards_generator.py

Generates questions about awards:
  - Who won the [Award] in [Year]?
  - Which player won the most [Award] awards?
  - Which league's player won the [Award] in [Year]?
"""

class AwardsTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for awards-related questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Awards'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Awards' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_award_winner_question,
            self._generate_most_awards_player_question,
            self._generate_award_league_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid awards trivia question after multiple attempts.")

    def _generate_award_winner_question(self):
        # Pick a random award and year
        query = text("""
            SELECT a.awardID, a.yearID, a.playerID, p.nameFirst, p.nameLast
            FROM awards a
            JOIN people p ON a.playerID = p.playerID
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No award winner found.")

        # Get 3 other random players
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
        question_text = f"Who won the {row.awardID} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_most_awards_player_question(self):
        # Find a player with the most awards of a certain type
        query = text("""
            SELECT a.awardID, a.playerID, p.nameFirst, p.nameLast, COUNT(*) as count
            FROM awards a
            JOIN people p ON a.playerID = p.playerID
            GROUP BY a.awardID, a.playerID
            HAVING count > 1
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No player with multiple awards found.")

        # Get 3 other random players
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
        question_text = f"Which player won the most {row.awardID} awards?"
        return question_text, dict(labeled), correct_letter

    def _generate_award_league_question(self):
        # Pick a random award and year, ask for the league
        query = text("""
            SELECT a.awardID, a.yearID, a.lgID
            FROM awards a
            WHERE a.lgID IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No award with league found.")

        # Get 3 other random leagues
        distractor_query = text("""
            SELECT DISTINCT lgID
            FROM awards
            WHERE lgID != :lgID
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'lgID': row.lgID}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor leagues found.")

        choices = [row.lgID] + [d.lgID for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, lg in labeled if lg == row.lgID)
        question_text = f"Which league's player won the {row.awardID} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter 