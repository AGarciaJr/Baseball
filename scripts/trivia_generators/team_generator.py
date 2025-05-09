from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class TeamTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for team-related questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Team Performance'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Team Performance' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)
            self.year_min, self.year_max = self._get_year_range()

    def _get_year_range(self):
        result = db.session.execute(
            text("SELECT MIN(yearID), MAX(yearID) FROM teams")
        ).fetchone()
        return result[0], result[1]

    def generate_question(self):
        """
        Randomly select a team question type and generate a question.
        """
        question_types = [
            self._generate_world_series_question,
            self._generate_team_record_question,
            self._generate_team_home_runs_question
        ]
        for _ in range(10):  # Try up to 10 times to get a valid question
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid team trivia question after multiple attempts.")

    def _generate_world_series_question(self):
        year = random.randint(self.year_min, self.year_max)
        query = text("""
            SELECT t.team_name
            FROM teams t
            JOIN seriespost sp ON t.teamID = sp.teamIDwinner
            WHERE sp.yearID = :year
            AND sp.round = 'WS'
            LIMIT 1
        """)
        result = db.session.execute(query, {'year': year})
        winner = result.fetchone()
        if not winner:
            raise Exception(f"No World Series data for year {year}")

        other_teams_query = text("""
            SELECT DISTINCT team_name
            FROM teams
            WHERE yearID = :year
            AND team_name != :winner
            ORDER BY RAND()
            LIMIT 3
        """)
        other_teams = db.session.execute(other_teams_query, {
            'year': year,
            'winner': winner.team_name
        }).fetchall()
        if len(other_teams) < 3:
            raise Exception(f"Not enough teams for year {year}")

        choices = [winner.team_name] + [t.team_name for t in other_teams]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == winner.team_name)
        question_text = f"Which team won the World Series in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_team_record_question(self):
        year = random.randint(self.year_min, self.year_max)
        query = text("""
            SELECT t.team_name, t.team_W, t.team_L
            FROM teams t
            WHERE t.yearID = :year
            ORDER BY t.team_W DESC
            LIMIT 4
        """)
        result = db.session.execute(query, {'year': year})
        teams = result.fetchall()
        if len(teams) < 4:
            raise Exception(f"Not enough teams for year {year}")

        choices = [f"{t.team_name} ({t.team_W}-{t.team_L})" for t in teams]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Which team had the best regular season record in {year}?"
        return question_text, dict(labeled), correct_letter

    def _generate_team_home_runs_question(self):
        year = random.randint(self.year_min, self.year_max)
        query = text("""
            SELECT t.team_name, SUM(b.b_HR) as total_hr
            FROM teams t
            JOIN batting b ON t.teamID = b.teamID AND t.yearID = b.yearId
            WHERE t.yearID = :year
            GROUP BY t.team_name
            ORDER BY total_hr DESC
            LIMIT 4
        """)
        result = db.session.execute(query, {'year': year})
        teams = result.fetchall()
        if len(teams) < 4:
            raise Exception(f"Not enough teams for year {year}")

        choices = [f"{t.team_name} ({t.total_hr} HR)" for t in teams]
        correct_name = choices[0]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, name in labeled if name == correct_name)
        question_text = f"Which team hit the most home runs in {year}?"
        return question_text, dict(labeled), correct_letter 