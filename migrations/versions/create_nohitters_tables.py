"""Create no-hitters tables

Revision ID: create_nohitters_tables
Revises: 45155ba4b4aa
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_nohitters_tables'
down_revision = '45155ba4b4aa'
branch_labels = None
depends_on = None

def upgrade():
    # Create no_hitters view
    op.execute("""
        CREATE OR REPLACE VIEW no_hitters AS
        SELECT DISTINCT
            p.pitching_ID,
            p.playerID,
            pe.nameFirst,
            pe.nameLast,
            p.yearID,
            p.teamID as pitcher_team,
            t.team_name as pitcher_team_name,
            p.p_CG,
            p.p_SHO,
            p.p_H,
            p.p_BB,
            p.p_SO,
            p.p_IPOuts,
            COALESCE(t2.teamID, t3.teamID) as opponent_team,
            COALESCE(t2.team_name, t3.team_name) as opponent_team_name
        FROM pitching p
        JOIN people pe ON p.playerID = pe.playerID
        JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
        -- Get other teams from the same year and league
        LEFT JOIN teams t2 ON t2.yearID = p.yearID 
            AND t2.lgID = t.lgID 
            AND t2.teamID != p.teamID
        -- Backup join in case the first one doesn't match
        LEFT JOIN teams t3 ON t3.yearID = p.yearID 
            AND t3.teamID != p.teamID
        WHERE p.p_H = 0 
        AND (p.p_CG = 1 OR p.p_IPOuts >= 27)  -- Include complete games and games with at least 9 innings pitched
        AND p.p_G > 0  -- Ensure the pitcher actually appeared in games
        GROUP BY p.pitching_ID  -- Group to avoid duplicates from the team joins
    """)

    # Create user_selections table
    op.create_table(
        'user_selections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(3), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
    )

def downgrade():
    op.execute("DROP VIEW IF EXISTS no_hitters")
    op.drop_table('user_selections') 