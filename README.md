# Baseball Trivia - Sandlot 2:The SQL

A web-based baseball trivia game that allows users to test their knowledge of baseball history, particularly focusing on no-hitters and team statistics.

## Features

- User authentication system with admin capabilities
- Baseball trivia game with scoring system
- Team selection and no-hitter information display
- Admin panel for user management

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the MariaDB database:
   ```sql
   CREATE DATABASE Sandlot2TheSQL;
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the database URL and secret key in `.env`

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

## Team Members

- [Your team members' names]

## Database Schema

The application uses the following main tables:
- Users (authentication and scoring)
- Teams (baseball team information)
- NoHitters (no-hitter game records)
- TriviaQuestions (trivia game content)

## Contributing

[Your contribution guidelines]

## License

[Your chosen license]
