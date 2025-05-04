CREATE TABLE trivia_questions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  question_text TEXT NOT NULL,
  choice_a VARCHAR(255),
  choice_b VARCHAR(255),
  choice_c VARCHAR(255),
  choice_d VARCHAR(255),
  correct_answer CHAR(1),  -- 'A', 'B', 'C', or 'D'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE trivia_answers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  question_id INT NOT NULL,
  selected_answer CHAR(1),
  is_correct BOOLEAN,
  answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (question_id) REFERENCES trivia_questions(id)
);
