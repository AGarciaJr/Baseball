CREATE TABLE no_hitters (
  id INT(11) NOT NULL AUTO_INCREMENT,
  game_date DATE NOT NULL,
  team_id INT(11) DEFAULT NULL,
  opponent_id INT(11) DEFAULT NULL,
  is_perfect TINYINT(1) DEFAULT 0,
  num_pitchers INT(11) DEFAULT NULL,
  notes TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  KEY team_id (team_id),
  KEY opponent_id (opponent_id),
  CONSTRAINT no_hitters_ibfk_1 FOREIGN KEY (team_id) REFERENCES teams (teams_ID),
  CONSTRAINT no_hitters_ibfk_2 FOREIGN KEY (opponent_id) REFERENCES teams (teams_ID)
);

CREATE TABLE no_hitter_pitchers (
  no_hitter_id INT(11) NOT NULL,
  player_id VARCHAR(9) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  order_num INT(11) DEFAULT NULL,
  PRIMARY KEY (no_hitter_id, player_id),
  KEY player_id (player_id),
  CONSTRAINT no_hitter_pitchers_ibfk_1 FOREIGN KEY (no_hitter_id) REFERENCES no_hitters (id),
  CONSTRAINT no_hitter_pitchers_ibfk_2 FOREIGN KEY (player_id) REFERENCES people (playerID)
);
