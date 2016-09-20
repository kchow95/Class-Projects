PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS user;
CREATE TABLE user (
	userid 		INTEGER PRIMARY KEY AUTOINCREMENT,
	firstname	TEXT NOT NULL,
	lastname	TEXT NOT NULL,
	created_at	DATE DEFAULT CURRENT_TIMESTAMP,
	username	TEXT UNIQUE NOT NULL,
	password	TEXT NOT NULL,
	current_player	INTEGER
);

DROP TABLE IF EXISTS player;
CREATE TABLE player (
   	playerid	INTEGER PRIMARY KEY AUTOINCREMENT,
    userid		INTEGER NOT NULL REFERENCES user,
    is_dead		INTEGER NOT NULL,
    lat			REAL	NOT NULL,
    lng			REAL	NOT NULL,
	is_werewolf	INTEGER NOT NULL DEFAULT 0,
	num_gold	INTEGER NOT NULL DEFAULT 0,
	game_id		INTEGER NOT NULL REFERENCES game
);

DROP TABLE IF EXISTS poi;
CREATE TABLE poi(
	poi_id	INTEGER PRIMARY KEY AUTOINCREMENT,
	lat 	REAL NOT NULL,
	lng 	REAL NOT NULL, 
	treasure_id		INTEGER REFERENCES treasure,
	safe_zone_id	INTEGER DEFAULT 0,
	radius	REAL NOT NULL
);

DROP TABLE IF EXISTS treasure;
CREATE TABLE treasure(
	treasure_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	itemid 		INTEGER NOT NULL REFERENCES item,
	quantity	INTEGER NOT NULL
);
DROP TABLE IF EXISTS playerlook;
CREATE TABLE playerlook (
	playerlookid 	INTEGER PRIMARY KEY AUTOINCREMENT,
	playerid		INTEGER NOT NULL,
	picture			TEXT NOT NULL
);

DROP TABLE IF EXISTS game;
CREATE TABLE game (
	gameid 	INTEGER PRIMARY KEY AUTOINCREMENT,
	adminid INTEGER NOT NULL REFERENCES user,
	status 	INTEGER NOT NULL DEFAULT 0,
	name	TEXT NOT NULL
);


DROP TABLE IF EXISTS achievement;
CREATE TABLE achievement (
	achievementid	INTEGER PRIMARY KEY AUTOINCREMENT,
	name			TEXT NOT NULL,
	description		TEXT NOT NULL
);

DROP TABLE IF EXISTS user_achievement;
CREATE TABLE user_achievement (
	userid			INTEGER,
	achievementid	INTEGER REFERENCES achievement,
	created_at		DATE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS item;
CREATE TABLE item (
	itemid 		INTEGER PRIMARY KEY AUTOINCREMENT,
	name 		TEXT NOT NULL,
	description TEXT
);

DROP TABLE IF EXISTS inventory;
CREATE TABLE inventory (
	playerid 	INTEGER REFERENCES user,
	itemid 		INTEGER REFERENCES item,
	quantity 	INTEGER,
	primary key (playerid, itemid)
);

-- used to store number of kills in a game --
DROP TABLE IF EXISTS player_stat;
CREATE TABLE player_stat (
	playerid 	INTEGER NOT NULL REFERENCES player,
	numKills	INTEGER
);

-- used to store number of kills historically
DROP TABLE IF EXISTS user_stat;
CREATE TABLE user_stat (
	userid 		INTEGER NOT NULL,
	statName	TEXT NOT NULL
);

-- creates a cascade delete so that all inventory items for the player
-- are automatically deleted

CREATE TRIGGER delete_inventory
BEFORE DELETE ON player
for each row
begin
	delete from inventory where playerid = 	old.playerid;
END;

CREATE INDEX playerindex ON inventory(playerid);
-- insert some data

PRAGMA foreign_keys = ON;

INSERT INTO user (userid, firstname, lastname, created_at, username, password) VALUES (1, 'Robert', 'Dickerson', '2014-08-30', 'rfdickerson', 'be121740bf988b2225a313fa1f107ca1');
INSERT INTO user (userid, firstname, lastname, created_at, username, password) VALUES (2, 'Abraham', 'Van Helsing', '2014-08-30', 'vanhelsing', 'be121740bf988b2225a313fa1f107ca1');

INSERT INTO user_stat VALUES(1, 'HEHEHEHEHE');


INSERT INTO game (gameid, adminid, status, name) VALUES (1, 2, 0, 'cool');
INSERT INTO game (gameid, adminid, status, name) VALUES (2, 2, 0, 'swag');
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (1, 1, 1, 38, 78, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (2, 2, 0, 24, 43, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (3, 1, 0, 10, 54, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (4, 2, 0, 9, 33, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (5, 1, 0, 88, 22, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (6, 2, 0, 6, 32, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (7, 1, 0, 5, 45, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (8, 2, 0, 44, 65, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (9, 1, 0, 23, 67, 1);
INSERT INTO player (playerid, userid, is_dead, lat, lng, game_id) VALUES (10, 2, 0, 99, 89, 2);

INSERT INTO player_stat VALUES(1, 23);


INSERT INTO achievement VALUES (1, 'Hair of the dog', 'Survive an attack by a werewolf');
INSERT INTO achievement VALUES (2, 'Top of the pack', 'Finish the game as a werewolf and receive the top number of kills');
INSERT INTO achievement VALUES (3, 'Children of the moon', 'Stay alive and win the game as a werewolf');
INSERT INTO achievement VALUES (4, 'It is never Lupus', 'Vote someone to be a werewolf, when they were a townsfolk');
INSERT INTO achievement VALUES (5, 'A hairy situation', 'Been near 3 werewolves at once.');
INSERT INTO achievement VALUES (6, 'Call in the Exterminators', 'Kill off all the werewolves in the game');
INSERT INTO achievement VALUES (7, 'Winner winner werewolf dinner', 'Win the game as human');
INSERT INTO achievement VALUES (8, 'freewins.com', 'win game by disconnecting');
INSERT INTO achievement VALUES (9, 'Buddy the werewolf', 'Kill two players near each other');
INSERT INTO achievement VALUES (10, 'Call in the Exterminators', 'Kill off all the werewolves in the game');
INSERT INTO achievement VALUES (11, 'Call in the Exterminators', 'Kill off all the werewolves in the game');
INSERT INTO achievement VALUES (12, 'Call in the Exterminators', 'Kill off all the werewolves in the game');

INSERT INTO user_achievement (userid, achievementid) VALUES (1, 1);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 2);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 3);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 4);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 5);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 6);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 8);
INSERT INTO user_achievement (userid, achievementid) VALUES (1, 9);
INSERT INTO user_achievement (userid, achievementid, created_at) VALUES (1, 11, '2014-09-02 05:54:38');

INSERT INTO user_achievement (userid, achievementid) VALUES (1, 12);

INSERT INTO item VALUES (1, 'Wolfsbane Potion', 'Protects the drinker from werewolf attacks');
INSERT INTO item VALUES (2, 'Blunderbuss', 'A muzzle-loading firearm with a short, large caliber barrel.');
INSERT INTO item VALUES (3, 'Invisibility Potion', 'Makes the imbiber invisible for a short period of time.');
INSERT INTO item VALUES (4, 'Silver Knife', 'A blade made from the purest of silvers');


INSERT INTO inventory VALUES (1, 2, 1);
INSERT INTO inventory VALUES (2, 1, 1);
INSERT INTO treasure (treasure_id, itemid, quantity) VALUES (1,1,1);
INSERT INTO poi (poi_id, lat, lng, treasure_id, safe_zone_id, radius) VALUES (2, 2.7 , 1.3, 1, 1, 1.0);




