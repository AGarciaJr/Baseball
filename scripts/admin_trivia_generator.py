from app import app, db
from sqlalchemy import text
from scripts.generate_trivia2 import generate_home_run_question

def generate_multiple_home_run_questions(count=20):
    with app.app_context():
        for _ in range(count):
            generate_home_run_question()
        print(f"✅ Generated {count} home run trivia questions")
