from abc import ABC, abstractmethod
from app import app, db
from sqlalchemy import text
import random
import logging

class BaseTriviaGenerator(ABC):
    """
    Abstract base class for trivia generators.
    Subclasses must implement generate_question().
    """
    def __init__(self, category_id, dry_run=False):
        """
        :param category_id: The ID of the trivia category for this generator.
        :param dry_run: If True, do not insert questions into the database.
        """
        self.category_id = category_id
        self.dry_run = dry_run
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate_question(self):
        """
        Generate a single trivia question.
        Must return a tuple of (question_text, choices, correct_answer)
        """
        pass

    def insert_question(self, question_text, choices, correct_answer):
        """
        Insert a generated question into the database, unless dry_run is True.
        Returns the question dict.
        """
        question = {
            'question': question_text,
            'choices': choices,
            'correct_answer': correct_answer
        }
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would insert: {question_text}")
            return question

        with app.app_context():
            insert_query = text("""
                INSERT INTO trivia_questions (
                    question_text, choice_a, choice_b, choice_c, choice_d, 
                    correct_answer, category_id
                ) VALUES (
                    :q, :a, :b, :c, :d, :correct, :category_id
                )
            """)

            try:
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
                question_id = result.lastrowid
                question['id'] = question_id
                self.logger.info(f"✅ Inserted: {question_text}")
            except Exception as e:
                self.logger.error(f"❌ Error inserting question: {str(e)}")
                raise
        return question

    def generate_batch(self, count=20):
        """
        Generate multiple questions and insert them (unless dry_run).
        Returns a list of question dicts.
        """
        generated_questions = []
        with app.app_context():
            for _ in range(count):
                try:
                    question_text, choices, correct_answer = self.generate_question()
                    question = self.insert_question(question_text, choices, correct_answer)
                    generated_questions.append(question)
                except Exception as e:
                    self.logger.warning(f"❌ Error generating question: {str(e)}")
                    continue
        return generated_questions 