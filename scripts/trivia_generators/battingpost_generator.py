from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class BattingPostTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for postseason batting questions.

    Generates questions about postseason batting:
      - Who hit the most home runs in the postseason in [Year]?
      - Which player had the most RBIs in the postseason in [Year]?
      - How many runs did [Player] score in the postseason in [Year]?
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Postseason Batting'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Postseason Batting' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_most_home_runs_post_question,
            self._generate_most_rbi_post_question,
            self._generate_runs_scored_post_question
        ]
        for _ in range(10):
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid battingpost trivia question after multiple attempts.")

    def _generate_most_home_runs_post_question(self):
        # Pick a random year
        year_query = text("SELECT DISTINCT yearId FROM battingpost ORDER BY RAND() LIMIT 1")
        year = db.session.execute(year_query).fetchone()
        if not year:
            raise Exception("No year found in battingpost table.")
        year = year.yearId

        # Get top 4 players by home runs in that year
        query = text("""
            SELECT p.nameFirst, p.nameLast, b.b_HR
            FROM battingpost b
            JOIN people p ON b.playerID = p.playerID
            WHERE b.yearId = :year AND b.b_HR IS NOT NULL
            ORDER BY b.b_HR DESC
            LIMIT 4
        """)
        players = db.session.execute(query, {'year': year}).fetchall()
        if len(players) < 4:
            raise Exception(f"Not enough players with home run data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Who hit the most home runs in the postseason in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_most_rbi_post_question(self):
        # Pick a random year
        year_query = text("SELECT DISTINCT yearId FROM battingpost ORDER BY RAND() LIMIT 1")
        year = db.session.execute(year_query).fetchone()
        if not year:
            raise Exception("No year found in battingpost table.")
        year = year.yearId

        # Get top 4 players by RBIs in that year
        query = text("""
            SELECT p.nameFirst, p.nameLast, b.b_RBI
            FROM battingpost b
            JOIN people p ON b.playerID = p.playerID
            WHERE b.yearId = :year AND b.b_RBI IS NOT NULL
            ORDER BY b.b_RBI DESC
            LIMIT 4
        """)
        players = db.session.execute(query, {'year': year}).fetchall()
        if len(players) < 4:
            raise Exception(f"Not enough players with RBI data for year {year}")

        choices = [f"{p.nameFirst} {p.nameLast}" for p in players]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Which player had the most RBIs in the postseason in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_runs_scored_post_question(self):
        # Pick a random player and year with a non-null runs scored
        query = text("""
            SELECT p.nameFirst, p.nameLast, b.yearId, b.b_R
            FROM battingpost b
            JOIN people p ON b.playerID = p.playerID
            WHERE b.b_R IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        player = db.session.execute(query).fetchone()
        if not player:
            raise Exception("No player with a valid runs scored found.")

        distractor_query = text("""
            SELECT DISTINCT b_R
            FROM battingpost
            WHERE b_R IS NOT NULL AND b_R != :runs
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'runs': player.b_R}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor run totals found.")

        choices = [str(player.b_R)] + [str(d.b_R) for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, runs in labeled if runs == str(player.b_R))
        question_text = f"How many runs did {player.nameFirst} {player.nameLast} score in the postseason in {player.yearId}?"
        return question_text, dict(labeled), correct_letter 