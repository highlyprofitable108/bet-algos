DB Schema

sports_data
|-- sport
|   |-- id (int, primary key)
|   |-- name (varchar(50), not null)
|
|-- league
|   |-- id (int, primary key)
|   |-- name (varchar(50), not null)
|   |-- sport_id (int, foreign key references sport(id))
|
|-- team
|   |-- id (int, primary key)
|   |-- name (varchar(50), not null)
|   |-- league_id (int, foreign key references league(id))
|
|-- game
|   |-- id (int, primary key)
|   |-- date (date, not null)
|   |-- home_team_id (int, foreign key references team(id))
|   |-- away_team_id (int, foreign key references team(id))
|   |-- league_id (int, foreign key references league(id))
|   |-- predicted_outcome (varchar(50))
|   |-- actual_outcome (varchar(50))
|
|-- player
|   |-- id (int, primary key)
|   |-- name (varchar(50), not null)
|   |-- team_id (int, foreign key references team(id))
|
|-- player_stat
|   |-- id (int, primary key)
|   |-- game_id (int, foreign key references game(id))
|   |-- player_id (int, foreign key references player(id))
|   |-- stat_type (varchar(50), not null)
|   |-- stat_value (int, not null)
|
|-- betting_odds
|   |-- id (int, primary key)
|   |-- game_id (int, foreign key references game(id))
|   |-- home_team_odds (float, not null)
|   |-- away_team_odds (float, not null)


Sure, I can help you get started on populating the database using SQLite. Here are the steps you can follow:

1. Create a new database file in SQLite. You can do this by running the following command in the terminal:

   ```
   sqlite3 sports_data.db
   ```

   This will create a new SQLite database file named `sports_data.db` in the current directory.

2. Create the necessary database tables using the schema provided in the previous message. You can do this by running the following SQL commands in the SQLite terminal:

   ```sql
   CREATE TABLE sport (
       id INTEGER PRIMARY KEY,
       name VARCHAR(50) NOT NULL
   );

   CREATE TABLE league (
       id INTEGER PRIMARY KEY,
       name VARCHAR(50) NOT NULL,
       sport_id INTEGER,
       FOREIGN KEY (sport_id) REFERENCES sport(id)
   );

   CREATE TABLE team (
       id INTEGER PRIMARY KEY,
       name VARCHAR(50) NOT NULL,
       league_id INTEGER,
       FOREIGN KEY (league_id) REFERENCES league(id)
   );

   CREATE TABLE game (
       id INTEGER PRIMARY KEY,
       date DATE NOT NULL,
       home_team_id INTEGER,
       away_team_id INTEGER,
       league_id INTEGER,
       predicted_outcome VARCHAR(50),
       actual_outcome VARCHAR(50),
       FOREIGN KEY (home_team_id) REFERENCES team(id),
       FOREIGN KEY (away_team_id) REFERENCES team(id),
       FOREIGN KEY (league_id) REFERENCES league(id)
   );

   CREATE TABLE player (
       id INTEGER PRIMARY KEY,
       name VARCHAR(50) NOT NULL,
       team_id INTEGER,
       FOREIGN KEY (team_id) REFERENCES team(id)
   );

   CREATE TABLE player_stat (
       id INTEGER PRIMARY KEY,
       game_id INTEGER,
       player_id INTEGER,
       stat_type VARCHAR(50) NOT NULL,
       stat_value INTEGER NOT NULL,
       FOREIGN KEY (game_id) REFERENCES game(id),
       FOREIGN KEY (player_id) REFERENCES player(id)
   );

   CREATE TABLE betting_odds (
       id INTEGER PRIMARY KEY,
       game_id INTEGER,
       home_team_odds FLOAT NOT NULL,
       away_team_odds FLOAT NOT NULL,
       FOREIGN KEY (game_id) REFERENCES game(id)
   );
   ```

3. Update the `read_data_file` function in `data_acquisition.py` to insert the parsed data into the appropriate tables in the database. You can use the `sqlite3` library in Python to execute SQL commands and insert data into the database.

4. Test the `read_data_file` function with sample data files to ensure that the data is being inserted into the database correctly.

Let me know if you have any questions or if there's anything else I can help with!
