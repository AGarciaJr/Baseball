from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

"""
managers_generator.py

Generates questions about managers:
  - Who managed the [Team] in [Year]?
  - How many games did [Manager] win managing the [Team] in [Year]?
  - What was the final rank of the [Team] managed by [Manager] in [Year]?
"""

class ManagersTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for manager-related questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Managers'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Managers' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_manager_team_year_question,
            self._generate_manager_wins_question,
            self._generate_manager_rank_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid managers trivia question after multiple attempts.")

    def _generate_manager_team_year_question(self):
        query = text("""
            SELECT m.yearID, m.teamID, m.playerID, p.nameFirst, p.nameLast
            FROM managers m
            JOIN people p ON m.playerID = p.playerID
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No manager found.")

        distractor_query = text("""
            SELECT nameFirst, nameLast
            FROM people
            WHERE playerID != :playerID
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'playerID': row.playerID}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor managers found.")

        choices = [f"{row.nameFirst} {row.nameLast}"] + [f"{d.nameFirst} {d.nameLast}" for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == f"{row.nameFirst} {row.nameLast}")
        question_text = f"Who managed the {row.teamID} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_manager_wins_question(self):
        query = text("""
            SELECT m.yearID, m.teamID, m.manager_W, p.nameFirst, p.nameLast
            FROM managers m
            JOIN people p ON m.playerID = p.playerID
            WHERE m.manager_W IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No manager with wins found.")

        distractor_query = text("""
            SELECT DISTINCT manager_W
            FROM managers
            WHERE manager_W IS NOT NULL AND manager_W != :manager_W
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'manager_W': row.manager_W}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor win totals found.")

        choices = [str(row.manager_W)] + [str(d.manager_W) for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, wins in labeled if wins == str(row.manager_W))
        question_text = f"How many games did {row.nameFirst} {row.nameLast} win managing the {row.teamID} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_manager_rank_question(self):
        query = text("""
            SELECT m.yearID, m.teamID, m.teamRank, p.nameFirst, p.nameLast
            FROM managers m
            JOIN people p ON m.playerID = p.playerID
            WHERE m.teamRank IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        row = db.session.execute(query).fetchone()
        if not row:
            raise Exception("No manager with rank found.")

        distractor_query = text("""
            SELECT DISTINCT teamRank
            FROM managers
            WHERE teamRank IS NOT NULL AND teamRank != :teamRank
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'teamRank': row.teamRank}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor ranks found.")

        choices = [str(row.teamRank)] + [str(d.teamRank) for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, rank in labeled if rank == str(row.teamRank))
        question_text = f"What was the final rank of the {row.teamID} managed by {row.nameFirst} {row.nameLast} in {row.yearID}?"
        return question_text, dict(labeled), correct_letter 