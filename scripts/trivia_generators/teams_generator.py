"""
teams_generator.py

Generates questions about teams:
  - Which city is home to the [Team Name]?
  - How many games did the [Team Name] win in [Year]?
  - Which team hit the most home runs in [Year]?
"""

from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class TeamsTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for team-related questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Teams'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Teams' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        question_types = [
            self._generate_team_location_question,
            self._generate_team_wins_question,
            self._generate_team_home_runs_question
        ]
        for _ in range(10):  # Try up to 10 times to get a valid question
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid teams trivia question after multiple attempts.")

    def _generate_team_location_question(self):
        # Pick a random team with a non-null city
        query = text("""
            SELECT DISTINCT team_name, park_name
            FROM teams
            WHERE park_name IS NOT NULL AND team_name IS NOT NULL AND park_name != ''
            ORDER BY RAND()
            LIMIT 1
        """)
        team = db.session.execute(query).fetchone()
        if not team:
            raise Exception("No team with a valid park/city found.")

        # Get 3 other random cities/parks
        distractor_query = text("""
            SELECT DISTINCT park_name
            FROM teams
            WHERE park_name IS NOT NULL AND park_name != :park_name AND park_name != ''
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'park_name': team.park_name}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor parks found.")

        choices = [team.park_name] + [d.park_name for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, city in labeled if city == team.park_name)
        question_text = f"Which city is home to the {team.team_name}?"
        return question_text, dict(labeled), correct_letter

    def _generate_team_wins_question(self):
        # Pick a random team and year with a non-null win total
        query = text("""
            SELECT team_name, yearID, team_W
            FROM teams
            WHERE team_W IS NOT NULL AND team_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        team = db.session.execute(query).fetchone()
        if not team:
            raise Exception("No team with a valid win total found.")

        # Get 3 other plausible win totals
        distractor_query = text("""
            SELECT DISTINCT team_W
            FROM teams
            WHERE team_W IS NOT NULL AND team_W != :team_W
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'team_W': team.team_W}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor win totals found.")

        choices = [str(team.team_W)] + [str(d.team_W) for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, wins in labeled if wins == str(team.team_W))
        question_text = f"How many games did the {team.team_name} win in {team.yearID}?"
        return question_text, dict(labeled), correct_letter

    def _generate_team_home_runs_question(self):
        # Pick a random year
        year_query = text("SELECT DISTINCT yearID FROM teams ORDER BY RAND() LIMIT 1")
        year = db.session.execute(year_query).fetchone()
        if not year:
            raise Exception("No year found in teams table.")
        year = year.yearID

        # Get top 4 teams by home runs in that year
        query = text("""
            SELECT team_name, team_HR
            FROM teams
            WHERE yearID = :year AND team_HR IS NOT NULL
            ORDER BY team_HR DESC
            LIMIT 4
        """)
        teams = db.session.execute(query, {'year': year}).fetchall()
        if len(teams) < 4:
            raise Exception(f"Not enough teams with home run data for year {year}")

        choices = [f"{t.team_name} ({t.team_HR} HR)" for t in teams]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Which team hit the most home runs in {year}?"
        return question_text, dict(labeled), correct_letter 