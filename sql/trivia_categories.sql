-- Create categories table
CREATE TABLE trivia_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add category_id to trivia_questions
ALTER TABLE trivia_questions
ADD COLUMN category_id INT,
ADD FOREIGN KEY (category_id) REFERENCES trivia_categories(id);

-- Insert initial categories
INSERT INTO trivia_categories (name, description) VALUES
('Home Runs', 'Questions about home run leaders and milestones'),
('Pitching', 'Questions about pitching statistics and achievements'),
('Team Performance', 'Questions about team records and championships'),
('Player Milestones', 'Questions about player career achievements'),
('Awards', 'Questions about major baseball awards'),
('Historical Firsts', 'Questions about baseball firsts and records'); 