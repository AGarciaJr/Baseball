import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
import logging
from sqlalchemy import text
from scripts.trivia_generators.pitching_generator import PitchingTriviaGenerator
from scripts.trivia_generators.team_generator import TeamTriviaGenerator
from scripts.trivia_generators.awards_generator import AwardsTriviaGenerator
from scripts.trivia_generators.managers_generator import ManagersTriviaGenerator
from scripts.trivia_generators.franchises_generator import FranchisesTriviaGenerator
from scripts.trivia_generators.divisions_generator import DivisionsTriviaGenerator
from scripts.trivia_generators.leagues_generator import LeaguesTriviaGenerator
from scripts.trivia_generators.parks_generator import ParksTriviaGenerator
from scripts.trivia_generators.people_generator import PeopleTriviaGenerator
from scripts.trivia_generators.schools_generator import SchoolsTriviaGenerator
from scripts.trivia_generators.no_hitters_generator import NoHittersTriviaGenerator
from scripts.trivia_generators.halloffame_generator import HallOfFameTriviaGenerator
from scripts.trivia_generators.seriespost_generator import SeriesPostTriviaGenerator
import argparse

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TriviaGenerator:
    def __init__(self):
        self.categories = {
            'teams': [
                'San Diego Padres',
                'Toronto Blue Jays',
                'Boston Red Sox',
                'Tampa Bay Rays',
                'Philadelphia Phillies'
            ],
            'positions': [
                'Third Base',
                'Shortstop',
                'Second Base',
                'First Base',
                'Catcher',
                'Outfield'
            ],
            'stats': [
                '30+ Home Runs',
                '100+ RBIs',
                '20+ Stolen Bases',
                '.300+ Batting Average',
                '100+ Runs Scored'
            ]
        }

    def generate_grid_question(self):
        """
        Generate a trivia question in Immaculate Grid format.
        Returns a tuple of (criteria1, criteria2, criteria3, correct_answers)
        """
        try:
            with app.app_context():
                # Example query to find players who meet specific criteria
                query = text("""
                    SELECT DISTINCT p.nameFirst, p.nameLast, t.name as team_name, 
                           f.POS as position, b.HR as home_runs, b.RBI as rbis,
                           b.SB as stolen_bases, b.AVG as batting_avg, b.R as runs
                    FROM people p
                    JOIN batting b ON p.playerID = b.playerID
                    JOIN teams t ON b.teamID = t.teamID
                    JOIN fielding f ON p.playerID = f.playerID AND b.yearID = f.yearID
                    WHERE b.yearID >= 1969  -- Modern era
                    LIMIT 1000
                """)
                
                result = db.session.execute(query)
                players = result.fetchall()
                
                # Process the results to create trivia questions
                # This is a placeholder - we'll implement the actual logic
                # based on the database schema and requirements
                
                return {
                    'criteria1': 'Team: San Diego Padres',
                    'criteria2': 'Position: Third Base',
                    'criteria3': 'Stats: 20+ Home Runs',
                    'correct_answers': []  # Will be populated with actual answers
                }
                
        except Exception as e:
            logger.error(f"Error generating trivia question: {e}")
            return None

    def validate_answer(self, player_name, criteria):
        """
        Validate if a player meets the given criteria
        """
        try:
            with app.app_context():
                # Example validation query
                query = text("""
                    SELECT COUNT(*) as count
                    FROM people p
                    JOIN batting b ON p.playerID = b.playerID
                    JOIN teams t ON b.teamID = t.teamID
                    JOIN fielding f ON p.playerID = f.playerID AND b.yearID = f.yearID
                    WHERE CONCAT(p.nameFirst, ' ', p.nameLast) = :player_name
                    AND t.name = :team_name
                    AND f.POS = :position
                    AND b.HR >= :min_hr
                """)
                
                result = db.session.execute(query, {
                    'player_name': player_name,
                    'team_name': criteria['team'],
                    'position': criteria['position'],
                    'min_hr': criteria['min_stats']['home_runs']
                })
                
                count = result.scalar()
                return count > 0
                
        except Exception as e:
            logger.error(f"Error validating answer: {e}")
            return False

def get_category_id(category_name):
    with app.app_context():
        result = db.session.execute(
            text("SELECT id FROM trivia_categories WHERE name = :name"),
            {"name": category_name}
        ).fetchone()
        return result.id if result else None

def generate_trivia(category=None, count=20):
    generators = {
        'Pitching': PitchingTriviaGenerator,
        'Team Performance': TeamTriviaGenerator,
        'Awards': AwardsTriviaGenerator,
        'Managers': ManagersTriviaGenerator,
        'Franchises': FranchisesTriviaGenerator,
        'Divisions': DivisionsTriviaGenerator,
        'Leagues': LeaguesTriviaGenerator,
        'Parks': ParksTriviaGenerator,
        'Player Biographies': PeopleTriviaGenerator,
        'Schools': SchoolsTriviaGenerator,
        'No-Hitters': NoHittersTriviaGenerator,
        'Hall of Fame': HallOfFameTriviaGenerator,
        'Postseason': SeriesPostTriviaGenerator,
    }

    generated_questions = []

    if category:
        if category not in generators:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {', '.join(generators.keys())}")
            return []
        
        generator = generators[category]()
        print(f"Generating {count} {category} questions...")
        generated_questions.extend(generator.generate_batch(count))
    else:
        # Generate questions from all categories
        for category_name, generator_class in generators.items():
            print(f"\nGenerating {count} {category_name} questions...")
            generator = generator_class()
            generated_questions.extend(generator.generate_batch(count))
    
    return generated_questions

def main():
    generator = TriviaGenerator()
    question = generator.generate_grid_question()
    if question:
        logger.info("Generated trivia question:")
        logger.info(f"Criteria 1: {question['criteria1']}")
        logger.info(f"Criteria 2: {question['criteria2']}")
        logger.info(f"Criteria 3: {question['criteria3']}")
    else:
        logger.error("Failed to generate trivia question")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate baseball trivia questions')
    parser.add_argument('--category', help='Category of questions to generate')
    parser.add_argument('--count', type=int, default=20, help='Number of questions to generate')
    
    args = parser.parse_args()
    generate_trivia(args.category, args.count) 