"""
people_generator.py

Generates questions about player biographies:
  - In which country was [Player] born?
  - In what year did [Player] make their MLB debut?
  - Which hand did [Player] bat with?
"""

from .base_generator import BaseTriviaGenerator
from app import app, db
from sqlalchemy import text
import random
import logging

class PeopleTriviaGenerator(BaseTriviaGenerator):
    """
    Trivia generator for player biographical questions.
    """
    def __init__(self, dry_run=False):
        with app.app_context():
            result = db.session.execute(
                text("SELECT id FROM trivia_categories WHERE name = 'Player Biographies'")
            ).fetchone()
            if not result:
                raise ValueError("Category 'Player Biographies' not found in trivia_categories table.")
            super().__init__(result.id, dry_run=dry_run)
            self.logger = logging.getLogger(self.__class__.__name__)

    def generate_question(self):
        """
        Randomly selects one of the available question types for player biographies.
        """
        question_types = [
            self._generate_birthplace_question,
            self._generate_debut_year_question,
            self._generate_bats_question
        ]
        for _ in range(10):  # Try up to 10 times to get a valid question
            generator = random.choice(question_types)
            try:
                return generator()
            except Exception as e:
                self.logger.warning(f"Retrying question generation: {str(e)}")
        raise Exception("Failed to generate a valid people trivia question after multiple attempts.")

    def _generate_birthplace_question(self):
        """
        Generates a question: In which country was [Player] born?
        """
        # Pick a random player with a non-null birthCountry
        query = text("""
            SELECT playerID, nameFirst, nameLast, birthCountry
            FROM people
            WHERE birthCountry IS NOT NULL AND birthCountry != ''
            ORDER BY RAND()
            LIMIT 1
        """)
        player = db.session.execute(query).fetchone()
        if not player:
            raise Exception("No player with a valid birth country found.")

        # Get 3 other random countries
        distractor_query = text("""
            SELECT DISTINCT birthCountry
            FROM people
            WHERE birthCountry IS NOT NULL AND birthCountry != :country AND birthCountry != ''
            ORDER BY RAND()
            LIMIT 3
        """)
        distractors = db.session.execute(distractor_query, {'country': player.birthCountry}).fetchall()
        if len(distractors) < 3:
            raise Exception("Not enough distractor countries found.")

        choices = [player.birthCountry] + [d.birthCountry for d in distractors]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, country in labeled if country == player.birthCountry)
        question_text = f"In which country was {player.nameFirst} {player.nameLast} born?"
        return question_text, dict(labeled), correct_letter

    def _generate_debut_year_question(self):
        """
        Generates a question: In what year did [Player] make their MLB debut?
        """
        # Pick a random player with a non-null debutDate
        query = text("""
            SELECT playerID, nameFirst, nameLast, debutDate
            FROM people
            WHERE debutDate IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        """)
        player = db.session.execute(query).fetchone()
        if not player or not player.debutDate:
            raise Exception("No player with a valid debut date found.")

        debut_year = player.debutDate.year
        # Get 3 other random years in plausible range
        distractor_years = set()
        while len(distractor_years) < 3:
            y = random.randint(1871, 2022)
            if y != debut_year:
                distractor_years.add(y)
        choices = [debut_year] + list(distractor_years)
        choices = [str(c) for c in choices]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, year in labeled if year == str(debut_year))
        question_text = f"In what year did {player.nameFirst} {player.nameLast} make their MLB debut?"
        return question_text, dict(labeled), correct_letter

    def _generate_bats_question(self):
        """
        Generates a question: Which hand did [Player] bat with?
        """
        # Pick a random player with a non-null bats value
        query = text("""
            SELECT playerID, nameFirst, nameLast, bats
            FROM people
            WHERE bats IS NOT NULL AND bats IN ('R', 'L', 'B')
            ORDER BY RAND()
            LIMIT 1
        """)
        player = db.session.execute(query).fetchone()
        if not player:
            raise Exception("No player with a valid bats value found.")

        bats_map = {'R': 'Right', 'L': 'Left', 'B': 'Both'}
        correct_bats = bats_map.get(player.bats, player.bats)
        distractors = [v for k, v in bats_map.items() if v != correct_bats]
        # If less than 3 distractors, add a random string
        while len(distractors) < 3:
            distractors.append(random.choice(['Switch', 'Unknown', 'Ambidextrous']))
        choices = [correct_bats] + distractors[:3]
        labeled = list(zip(['A', 'B', 'C', 'D'], random.sample(choices, 4)))
        correct_letter = next(label for label, val in labeled if val == correct_bats)
        question_text = f"Which hand did {player.nameFirst} {player.nameLast} bat with?"
        return question_text, dict(labeled), correct_letter 