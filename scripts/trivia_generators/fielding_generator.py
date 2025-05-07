from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class FieldingTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for fielding-related questions.

    Generates questions about fielding:
      - Who played the most games in the field in [Year]?
      - Who committed the most errors in the field in [Year]?
      - What position did [Player] play in [Year]?
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Fielding'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Fielding' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_most_games_fielded_question,
            self._generate_most_errors_question,
            self._generate_position_played_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid fielding trivia question after multiple attempts.")

    def _generate_most_games_fielded_question(self):
        # Pick a random year
        year_query = text("SELECT DISTINCT yearID FROM fielding ORDER BY RAND() LIMIT 1")
        year = db.session.execute(year_query).fetchone()
        if not year:
            raise Exception("No year found in fielding table.")
        year = year.yearID

        # Get top 4 players by games fielded in that year
        query = text("""
            SELECT p.nameFirst, p.nameLast, f.f_G
            FROM fielding f
            JOIN people p ON f.playerID = p.playerID
            WHERE f.yearID = :year AND f.f_G IS NOT NULL
            ORDER BY f.f_G DESC
            LIMIT 4
        """)
        players = db.session.execute(query, {'year': year}).fetchall()
        if len(players) < 4:
            raise Exception(f"Not enough players with games fielded data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Who played the most games in the field in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_most_errors_question(self):
        # Pick a random year
        year_query = text("SELECT DISTINCT yearID FROM fielding ORDER BY RAND() LIMIT 1")
        year = db.session.execute(year_query).fetchone()
        if not year:
            raise Exception("No year found in fielding table.")
        year = year.yearID

        # Get top 4 players by errors in that year
        query = text("""
            SELECT p.nameFirst, p.nameLast, f.f_E
            FROM fielding f
            JOIN people p ON f.playerID = p.playerID
            WHERE f.yearID = :year AND f.f_E IS NOT NULL
            ORDER BY f.f_E DESC
            LIMIT 4
        """)
        players = db.session.execute(query, {'year': year}).fetchall()
        if len(players) < 4:
            raise Exception(f"Not enough players with error data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Who committed the most errors in the field in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_position_played_question(self):
        # Pick a random player and year with a non-null position
        query = text("""
            SELECT p.nameFirst, p.nameLast, f.yearID, f.position
            FROM fielding f
            JOIN people p ON f.playerID = p.playerID
            WHERE f.position IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        player = db.session.execute(query).fetchone()
        if not player:
            raise Exception("No player with a valid position found.")

        distractor_query = text("""
            SELECT DISTINCT position
            FROM fielding
            WHERE position IS NOT NULL AND position != :position
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'position': player.position}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor positions found.")

        choices = [player.position] + [d.position for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, pos in labeled if pos == player.position)
        question_text = f"What position did {player.nameFirst} {player.nameLast} play in {player.yearID}?"
        return question_text, dict(labeled), correct_letter 