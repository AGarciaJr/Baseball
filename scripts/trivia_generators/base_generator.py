from abc import ABC, abstractmethod
from app import app, db
from sqlalchemy import text
import random

class BaseTriviaGenerator(ABC):
    def __init__(self, category_id):
        self.category_id = category_id

    @abstractmethod
    def generate_question(self):
        """Generate a single trivia question. Must return a tuple of (question_text, choices, correct_answer)"""
        pass

    def insert_question(self, question_text, choices, correct_answer):
        """Insert a generated question into the database"""
        with app.app_context():
            insert_query = text("""
                INSERT INTO trivia_questions (
                    question_text, choice_a, choice_b, choice_c, choice_d, 
                    correct_answer, category_id
                ) VALUES (
                    :q, :a, :b, :c, :d, :correct, :category_id
                )
            """)

            result = db.session.execute(insert_query, {
                'q': question_text,
                'a': choices['A'],
                'b': choices['B'],
                'c': choices['C'],
                'd': choices['D'],
                'correct': correct_answer,
                'category_id': self.category_id
            })
            db.session.commit()
            
            # Get the inserted question
            question_id = result.lastrowid
            question = {
                'id': question_id,
                'question': question_text,
                'choices': choices,
                'correct_answer': correct_answer
            }
            
            print(f"✅ Inserted: {question_text}")
            return question

    def generate_batch(self, count=20):
        """Generate multiple questions"""
        generated_questions = []
        with app.app_context():
            for _ in range(count):
                try:
                    question_text, choices, correct_answer = self.generate_question()
                    question = self.insert_question(question_text, choices, correct_answer)
                    generated_questions.append(question)
                except Exception as e:
                    print(f"❌ Error generating question: {str(e)}")
                    continue
        return generated_questions 