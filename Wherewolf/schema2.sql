CREATE EXTENSION cube;
CREATE EXTENSION earthdistance;

DROP TABLE IF EXISTS gameuser cascade;
CREATE TABLE gameuser (
	user_id 	serial primary key,
	firstname	varchar(80) NOT NULL,
	lastname	varchar(80) NOT NULL,
	created_at	timestamp DEFAULT CURRENT_TIMESTAMP,
	username	varchar(80) UNIQUE NOT NULL,
	password	varchar(128) NOT NULL,
	current_player  integer
);

DROP TABLE IF EXISTS game cascade;
CREATE TABLE game (
	game_id 	serial primary key,
	admin_id 	int NOT NULL REFERENCES gameuser,
	status 		int NOT NULL DEFAULT 0,
	name		varchar(80) NOT NULL,
	description	text
);

DROP TABLE IF EXISTS player cascade;
CREATE TABLE player (
   	player_id	serial primary key,
   	is_dead		INTEGER NOT NULL,
  	lat		FLOAT	NOT NULL,
    	lng		FLOAT	NOT NULL,
	is_werewolf	INTEGER NOT NULL DEFAULT 0,
	num_gold	INTEGER NOT NULL DEFAULT 0,
	game_id		INTEGER REFERENCES game
);
--tell dora
DROP TABLE IF EXISTS gametime cascade;
CREATE TABLE gametime (
	game_id int NOT NULL REFERENCES game,
	time 	time,
	night 	time DEFAULT '19:00:00',
	day		time DEFAULT '07:00:00'
);


-----------create table for points of interest
DROP TABLE IF EXISTS landmark cascade;
CREATE TABLE landmark (
	landmark_id	serial primary key,
	lat		float NOT NULL,
	lng		float NOT NULL,
	radius		float NOT NULL,
	type		int NOT NULL,
	game_id		int NOT NULL REFERENCES game,
	is_active 	int NOT NULL DEFAULT 0,
	created_at	date
);

DROP TABLE IF EXISTS achievement cascade;
CREATE TABLE achievement (
	achievement_id	serial primary key,
	name		varchar(80) NOT NULL,
	description	text NOT NULL
);

DROP TABLE IF EXISTS user_achievement cascade;
CREATE TABLE user_achievement (
	user_id		INTEGER references gameuser,
	achievement_id	INTEGER references achievement,
	created_at	timestamp
);
--tell dora
DROP TABLE IF EXISTS item cascade;
CREATE TABLE item (
	itemid 		serial primary key,
	name 		varchar(80) NOT NULL,
	description 	TEXT
);

DROP TABLE IF EXISTS inventory cascade;
CREATE TABLE inventory (
	player_id 	INTEGER REFERENCES player,
	itemid 		INTEGER REFERENCES item,
	quantity 	INTEGER,
	primary key (player_id, itemid)
);


DROP TABLE IF EXISTS treasure cascade;
CREATE TABLE treasure(
	landmark_id	INTEGER REFERENCES landmark,
	item_id	 	INTEGER references item,
	quantity  	INTEGER NOT NULL,
	primary key (landmark_id, item_id)
);

-- used to store number of kills in a game --
DROP TABLE IF EXISTS player_stat cascade;
CREATE TABLE player_stat (
	player_id 	INTEGER NOT NULL REFERENCES player,
	stat_name	varchar(80) NOT NULL,
	stat_value	varchar(80) NOT NULL,
    primary key (player_id, stat_name)
);
DROP TABLE IF EXISTS player_attributes cascade;
CREATE TABLE player_attributes(
	player_id	INTEGER primary key REFERENCES player,
	damage 		integer DEFAULT 1,
	HP			integer DEFAULT 10
);


-- used to store number of kills historically
DROP TABLE IF EXISTS user_stat cascade;
CREATE TABLE user_stat (
	user_id 	INTEGER NOT NULL,
	stat_name	varchar(80) NOT NULL,
	stat_value	varchar(80) NOT NULL,
        primary key (user_id, stat_name)
);

DROP TABLE IF EXISTS vote cascade;
CREATE TABLE vote (
       vote_id		serial primary key,
       game_id      integer references game,
       player_id    integer references player,
       target_id  	integer references player,
       cast_date	timestamp
);
DROP TABLE IF EXISTS weapons cascade;
CREATE TABLE weapons(
	item_id		integer primary key REFERENCES item,
	damage 		integer
);
DROP TABLE IF EXISTS armor cascade;
CREATE TABLE armor(
	item_id	integer primary key REFERENCES item,
	armor_rating integer
);




CREATE INDEX playerindex ON inventory(player_id);
CREATE INDEX username ON gameuser(username);
CREATE INDEX indexitemname ON item(name);

-- adds an index so our lookups based on position will be exponentially faster
CREATE INDEX pos_index ON player USING gist (ll_to_earth(lat, lng));
-- insert some data

-- functions



-- INSERT INTO gameuser (user_id, firstname, lastname, created_at, username, password) VALUES (1, 'Robert', 'Dickerson', timestamp '2004-10-19' , 'rfdickerson', 'be121740bf988b2225a313fa1f107ca1');
-- INSERT INTO gameuser (user_id, firstname, lastname, created_at, username, password) VALUES (2, 'Abraham', 'Van Helsing', timestamp '2012-8-20 10:23:12', 'vanhelsing', 'be121740bf988b2225a313fa1f107ca1');

-- INSERT INTO game (admin_id, status, name) VALUES (1, 0, 'TheGame');

-- INSERT INTO player (player_id, is_dead, lat, lng, game_id) VALUES (1, 0, 38, 78, 1);
-- INSERT INTO player (player_id, is_dead, lat, lng, game_id) VALUES (2, 0, 38.01, 77.01, 1);

-- UPDATE gameuser SET current_player=1 WHERE username='rfdickerson'; 
-- UPDATE gameuser SET current_player=2 WHERE username='vanhelsing'; 

INSERT INTO achievement VALUES (1, 'Hair of the dog', 'Survive an attack by a werewolf');
INSERT INTO achievement VALUES (2, 'Top of the pack', 'Finish the game as a werewolf and receive the top number of kills');
INSERT INTO achievement VALUES (3, 'Children of the moon', 'Stay alive and win the game as a werewolf');
INSERT INTO achievement VALUES (4, 'It is never Lupus', 'Vote someone to be a werewolf, when they were a townsfolk');
INSERT INTO achievement VALUES (5, 'A hairy situation', 'Been near 3 werewolves at once.');
INSERT INTO achievement VALUES (6, 'Call in the Exterminators', 'Kill off all the werewolves in the game');

-- INSERT INTO user_achievement (user_id, achievement_id, created_at) VALUES (1, 1, timestamp '2014-06-06 01:01:01');
-- INSERT INTO user_achievement (user_id, achievement_id, created_at) VALUES (1, 2, timestamp '2014-08-08 03:03:03');


--tell dora
INSERT INTO item VALUES (1, 'Wolfsbane Potion', 'Protects the drinker from werewolf attacks');
INSERT INTO item VALUES (2, 'Blunderbuss', 'A muzzle-loading firearm with a short, large caliber barrel.');
INSERT INTO item VALUES (3, 'Invisibility Potion', 'Makes the imbiber invisible for a short period of time.');
INSERT INTO item VALUES (5, 'Cleaver', 'The weapon of choice for a butcher');
INSERT INTO item VALUES (6, 'Tunic', 'For the poor men');
INSERT INTO item VALUES (7, 'Leather', 'Simple armor');
INSERT INTO item VALUES (8, 'Chain Mail', 'Protects against the claws of an attacker');
INSERT INTO item VALUES (9, 'Silver Plating', 'Your shining armor');
INSERT INTO item VALUES (10, 'Fists', 'Weaponless');
INSERT INTO item VALUES (11, 'Silver Knife', 'small knife');

INSERT INTO weapons VALUES (2, 10);
INSERT INTO weapons VALUES (5, 6);
INSERT INTO weapons VALUES (10, 0);
INSERT INTO weapons VALUES (11, 3);

INSERT INTO armor VALUES (6, 0);
INSERT INTO armor VALUES (7, 1);
INSERT INTO armor VALUES (8, 2);
INSERT INTO armor VALUES (9, 3);






-- INSERT INTO inventory VALUES (1, 2, 1);
-- INSERT INTO inventory VALUES (2, 1, 1);