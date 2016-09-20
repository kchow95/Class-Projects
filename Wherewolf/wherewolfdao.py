import psycopg2
import md5
from random import randrange
import random
from random import shuffle



class UserAlreadyExistsException(Exception):
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return 'Exception: ' + self.err
        
class NoUserExistsException(Exception):
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return 'Exception: ' + self.err
        
class BadArgumentsException(Exception):
    """Exception for entering bad arguments"""
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return 'Exception: ' + self.err

class WherewolfDao:

    def __init__(self, dbname='wherewolf', pgusername='kchow95', pgpasswd='4zzvanou', pghost= 'wherewolf.cslnvqxv85qz.us-west-2.rds.amazonaws.com'):
        self.dbname = dbname
        self.pgusername = pgusername
        self.pgpasswd = pgpasswd
        self.pghost = pghost
        print ('connection to database {}, user: {}, password: {}'.format(dbname, pgusername, pgpasswd))

    def get_db(self):
        return psycopg2.connect(database=self.dbname,user=self.pgusername,password=self.pgpasswd, host = self.pghost)

    def create_user(self, username, password, firstname, lastname):
        """ registers a new player in the system """
        conn = self.get_db()
        with conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) from gameuser WHERE username=%s',(username,))
            n = int(c.fetchone()[0])
            # print 'num of rfdickersons is ' + str(n)
            if n == 0:
                hashedpass = md5.new(password).hexdigest()
                c.execute('INSERT INTO gameuser (username, password, firstname, lastname) VALUES (%s,%s,%s,%s)', 
                          (username, password, firstname, lastname))
                conn.commit()
            else:
                return -1
                #raise UserAlreadyExistsException('{} user already exists'.format((username)) )

    def get_games(self):
        conn = self.get_db()
        games = []
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT game_id, name, description from game')
            cur.execute(cmd)
            for row in cur.fetchall():
                d = {}
                d["game_id"] = row[0]
                d["name"] = row[1]
                d["description"] = row[2]
                games.append(d)
        print(games)
        return games
        
    def check_password(self, username, password):
        """ return true if password checks out """
        conn = self.get_db()
        with conn:
            c = conn.cursor()
            sql = ('select password from gameuser where username=%s')
            c.execute(sql,(username,))
            hashedpass = md5.new(password).hexdigest()
            u = c.fetchone()
            if u == None:
                raise NoUserExistsException(username)
            # print 'database contains {}, entered password was {}'.format(u[0],hashedpass)
            print u[0]
            return u[0] == hashedpass
        
    def set_location(self, username, lat, lng):
        conn = self.get_db()
        print lat
        print username
        print lng
        with conn:
            cur = conn.cursor()
            sql = ('update player set lat=%s, lng=%s '
                   'where player_id=(select current_player from gameuser '
                   'where username=%s)')
            cur.execute(sql, (lat, lng, username))
            conn.commit()
        return True

    def set_adminid(self, admin_id, game_name):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sql = ('update game set admin_id=%s where name=%s')
            cur.execute(sql, (admin_id, game_name))
            conn.commit()

    def get_location(self, username):
        conn = self.get_db()
        result = {}
        with conn:
            c = conn.cursor()
            sql = ('select player_id, lat, lng from player, gameuser '
                   'where player.player_id = gameuser.current_player '
                   'and gameuser.username=%s')
            c.execute(sql, (username,))
            row = c.fetchone()
            result["playerid"] = row[0]
            result["lat"] = row[1]
            result["lng"] = row[2]
        return result

    def get_userid(self, username):
        conn = self.get_db()
        result = {}
        with conn: 
            c = conn.cursor()
            sql = ('select user_id from gameuser where username=%s')
            c.execute(sql, (username,))
            row = c.fetchone()[0]
        return row

        
    def get_alive_nearby(self, username, game_id, radius): 
        ''' returns all alive players near a player '''
        conn = self.get_db()
        result = []
        with conn:
            c = conn.cursor()
            sql_location = ('select lat, lng from player, gameuser where '
                           'player.player_id = gameuser.current_player '
                           'and gameuser.username=%s')
            c.execute(sql_location, (username,))
            location = c.fetchone()

            if location == None:
                return result

            # using the radius for lookups now
            sql = ('select player_id, '
                   'earth_distance( ll_to_earth(player.lat, player.lng), '
                   'll_to_earth(%s,%s) ) '
                   'from player where '
                   'earth_box(ll_to_earth(%s,%s),%s) '
                   '@> ll_to_earth(player.lat, player.lng) '
                   'and game_id=%s '
                   'and is_werewolf = 0 '
                   'and is_dead = 0')

            # sql = ('select username, player_id, point( '
            #       '(select lng from player, gameuser '
            #       'where player.player_id=gameuser.current_player '
            #       'and gameuser.username=%s), '
            #       '(select lat from player, gameuser '
            #       'where player.player_id=gameuser.current_player '
            #       'and gameuser.username=%s)) '
            #       '<@> point(lng, lat)::point as distance, '
            #       'is_werewolf '
            #       'from player, gameuser where game_id=%s '
            #       'and is_dead=0 '
            #       'and gameuser.current_player=player.player_id '
            #       'order by distance')
            # print sql

            c.execute(sql, (location[0], location[1], 
                            location[0], location[1], 
                            radius, game_id))
            for row in c.fetchall():
                d = {}
                d["player_id"] = row[0]
                d["distance"] = row[1]
                #d["distance"] = row[1]
                #d["is_werewolf"] = row[2]
                result.append(d)
        return result
                   
        
    def add_item(self, username, itemname):
        conn = self.get_db()
        with conn:
            cur=conn.cursor()

            cmdupdate = ('update inventory set quantity=quantity+1'
                         'where itemid=(select itemid from item where name=%s)' 
                         'and playerid='
                         '(select current_player from gameuser where username=%s);')
            cmd = ('insert into inventory (playerid, itemid, quantity)' 
                   'select (select current_player from gameuser where username=%s) as cplayer,'
                   '(select itemid from item where name=%s) as item,' 
                   '1 where not exists' 
                   '(select 1 from inventory where itemid=(select itemid from item where name=%s)' 
                   'and playerid=(select current_player from gameuser where username=%s))')
            cur.execute(cmdupdate + cmd, (itemname, username, username, itemname, itemname, username))

            conn.commit()

 
    def remove_item(self, username, itemname):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('update inventory set quantity=quantity-1 where ' 
                   'itemid=(select itemid from item where name=%s) and ' 
                   'player_id=(select current_player from gameuser where username=%s);')
            cmddelete = ('delete from inventory where itemid=(select itemid from item where name=%s)' 
                         'and player_id=(select current_player from gameuser where username=%s) '
                         'and quantity < 1;')
            cur.execute(cmd + cmddelete, (itemname, username, itemname, username))
            conn.commit()


    def get_items(self, username):
        conn = self.get_db()
        items = []
        with conn:
            c = conn.cursor()
            sql = ('select item.name, item.description, quantity '
                   'from item, inventory, gameuser where '
                   'inventory.itemid = item.itemid and '
                   'gameuser.current_player=inventory.player_id and '
                   'gameuser.username=%s')
            c.execute(sql, (username,))
            for item in c.fetchall():
                d = {}
                d["name"] = item[0]
                d["description"] = item[1]
                d["quantity"] = item[2]
                items.append(d)
        return items

        
    def award_achievement(self, username, achievementname):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('insert into user_achievement (user_id, achievement_id, created_at) '
                   'values ((select user_id from gameuser where username=%s), '
                   '(select achievement_id from achievement where name=%s), now());')
            cur.execute(cmd, (username, achievementname))
            conn.commit()

        
    def get_achievements(self, username):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('select name, description, created_at from achievement, user_achievement '
                   'where achievement.achievement_id = user_achievement.achievement_id '
                   'and user_achievement.user_id = '
                   '(select user_id from gameuser where username=%s);')
            cur.execute(cmd, (username,))
            achievements = []
            for row in cur.fetchall():
                d = {}
                d["name"] = row[0]
                d["description"] = row[1]
                d["created_at"] = row[2]
                achievements.append(d)
        return achievements

    def set_dead(self, username):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('update player set is_dead=1 '
                   'where player_id='
                   '(select current_player from gameuser where username=%s);')
            cur.execute(cmd, (username,))
            conn.commit()


    def get_players(self, gameid):
        conn = self.get_db()
        players = []
        with conn:
            cur = conn.cursor()
            cmd = ('select player_id, is_dead, lat, lng, is_werewolf from player '
                   ' where game_id=%s;')
            cur.execute(cmd, (gameid,))
            for row in cur.fetchall():
                p = {}
                p["playerid"] = row[0]
                p["is_dead"] = row[1]
                p["lat"] = row[2]
                p["lng"] = row[3]
                p["is_werewolf"] = row[4]
                players.append(p)
        return players

    def get_user_stats(self, username):
        pass
        
        
    def get_player_stats(self, username):
        pass

    # game methods    
    def join_game(self, username, gameid):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('INSERT INTO player ( is_dead, lat, lng, game_id) '
                   'VALUES ( %s, %s, %s, %s) returning player_id')
            cmd2 = ('update gameuser set current_player=%s where username=%s')
            cmd4 = ('INSERT INTO player_attributes (player_id) VALUES (%s)')
            cur.execute(cmd,( 0, 0, 0, gameid))
            playerid = cur.fetchone()[0]
            cur.execute(cmd2, (playerid, username));
            cur.execute(cmd4, (playerid,))
            conn.commit()

    
    def leave_game(self, username, game_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmdInventory = ('DELETE FROM inventory where player_id = (select current_player from gameuser where username = %s)')
            cmdPlayerstat = ('DELETE FROM player_stat where player_id = (select current_player from gameuser where username = %s)')
            cmdVote = ('DELETE FROM vote where player_id = (select current_player from gameuser where username = %s)')
            cmdVote2 = ('DELETE FROM vote where target_id = (select current_player from gameuser where username = %s)')
            cmdAttributes = ('DELETE FROM player_attributes where player_id = (select current_player from gameuser where username = %s)')
            cmd1 = '''UPDATE gameuser set current_player = null where username=%s'''
            cmdPlayer = ('DELETE FROM player where player_id = (select current_player from gameuser where username = %s)')
            cur.execute(cmdInventory, (username,))
            cur.execute(cmdPlayerstat, (username,))
            cur.execute(cmdVote, (username,))
            cur.execute(cmdVote2, (username,))
            cur.execute(cmdAttributes, (username,))
            cur.execute(cmdPlayer, (username,))
            cur.execute(cmd1, (username,)) 

            conn.commit()
        
        
    def create_game(self, username, gamename, gamedescription):
        ''' returns the game id for that game '''
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('INSERT INTO game (admin_id, name, description) VALUES ( '
                   '(SELECT user_id FROM gameuser where username=%s), '
                   '%s, %s) returning game_id')
            cur.execute(cmd,(username, gamename, gamedescription))
            game_id = cur.fetchone()[0]
            conn.commit()
            return game_id
    def get_current_ballot(self, game_id):
        conn = self.get_db()
        player_stats = []
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT target_id, COUNT(*) from vote where game_id=%s group by target_id')
            print cmd
            cur.execute(cmd, (game_id,))

            for row in cur.fetchall():
                d = {}
                d["player_id"] = row[0]
                d["votes"] = row[1]
                player_stats.append(d)
        return player_stats
    def check_if_admin(self, user_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT admin_id from game where admin_id=%s', (user_id,))
        return cur.fetchone() == None
    def check_if_game_admin(self, user_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT game_id from game where admin_id=%s', (user_id,))
        return cur.fetchone()
    def delete_game(self, game_id):                   
        conn = self.get_db()
        
        with conn:
            cur = conn.cursor()
            insertsql = ('delete from player where game_id=%s')
            
            cur.execute(insertsql,(game_id,))
            conn.commit()
    def check_lobby_mode(self, game_id):
        conn = self.get_db()
        with conn:
            c = conn.cursor()
            sqlquery = ('select status from game where game_id=%s')
            cur = conn.cursor()
            cur.execute(sqlquery, (game_id,))
            status = cur.fetchone()[0]
        return status
    def check_if_in_game(self, user_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT current_player from gameuser where user_id=%s', (user_id,))
        #if none, not in game
        return cur.fetchone() == (None,)   
    def game_info(self, game_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = '''SELECT game_id, admin_id, status, name from game where game_id=%s'''
            cmdPlayers = ('SELECT username from gameuser join player on gameuser.current_player = player.player_id where game_id = %s and is_dead = 0')
            'select damage from inventory join item on inventory.itemid = item.itemid join weapons on weapons.item_id = item.itemid where inventory.player_id =%s'
            cur.execute(cmd, (game_id,))

            row = cur.fetchone()
            d = {}
            cur.execute(cmdPlayers, (game_id,))
            player = cur.fetchall()
            d["alive_players"] = player
            d["game_id"] = row[0]
            d["admin_id"] = row[1]
            d["status"] = row[2]
            d["name"] = row[3]
            return d
    def is_game_over_v(self, game_id): #did villager win
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT username from gameuser join player on gameuser.current_player = player.player_id where game_id = %s and is_dead = 0 and is_werewolf = 1')
            cur.execute(cmd, (game_id,))

            if cur.fetchone() == None:
                return True
            else:
                return False
    def is_game_over_w(self, game_id): #did did werewolves win
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT username from gameuser join player on gameuser.current_player = player.player_id where game_id = %s and is_dead = 0 and is_werewolf = 0')
            cur.execute(cmd, (game_id,))

            if cur.fetchone() == None:
                return True
            else:
                return False
    def count_players(self, game_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT Count (*) from player where game_id = %s')
            cur.execute(cmd, (game_id,))
            counted = int(cur.fetchone()[0])
            return counted

    def get_games(self):
        conn = self.get_db()
        games = []
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT game_id, name, description from game')
            cur.execute(cmd)
            for row in cur.fetchall():
                d = {}
                d["game_id"] = row[0]
                d["name"] = row[1]
                d["description"] = row[2]
                games.append(d)
        return games

    def count_games(self):
        conn = self.get_db()
        count = 0
        games = []
        with conn:
            cur = conn.cursor()
            cmd = ('SELECT game_id, name, description from game')
            cur.execute(cmd)
            for row in cur.fetchall():
                count = count + 1
        return count

            
    def set_game_status(self, game_id, status):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            cmd = ('UPDATE game set status=%s '
                   'where game_id=%s')
            cur.execute(cmd, (game_id, status))
        

    def vote(self, game_id, player_id, target_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            insertsql = ('insert into vote (game_id, player_id, target_id, cast_date) VALUES (%s, %s, %s, now())')
            sql = ('insert into vote '
                   '(game_id, player_id, target_id, cast_date) '
                   'values ( %s,'
                   '(select current_player from gameuser where username=%s), '
                   '(select current_player from gameuser where username=%s), '
                   'now())')
            cur.execute(insertsql, (game_id, player_id, target_id))
            conn.commit()
            
    
    def clear_tables(self):
        conn = self.get_db()
        with conn:
            c = conn.cursor()
            c.execute('truncate gameuser cascade')
            c.execute('truncate player cascade')
            c.execute('truncate user_achievement cascade')
            conn.commit()
    #tell dora
    def add_stats(self):
        conn = self.get_db()
        with conn:
            c = conn.cursor()
    #get base hp
    def get_HP(self, player_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlArmor = ('select HP from player_attributes where player_id =%s')
            cur.execute(sqlArmor, (player_id,))
            HPtotal = cur.fetchone()[0]
        return int(HPtotal)
    #get base damage
    def get_damage(self, player_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlArmor = ('select damage from player_attributes where player_id =%s')
            cur.execute(sqlArmor, (player_id,))
            damageTotal = cur.fetchone()[0]
        return int(damageTotal)
    #set the basewerewolf statsif they are a werewolf
    def set_baseWerewolf(self, username):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlplayer_id = ('SELECT current_player from gameuser WHERE username =%s')
            cur.execute(sqlplayer_id, (username,))
            player_id = int(cur.fetchone()[0])
            sqlWerewolf = ('select is_werewolf from player where player_id = %s')
            cur.execute(sqlWerewolf,(player_id,))
            werewolfRank = int(cur.fetchone()[0])

            if werewolfRank == 0:
                return False
            elif werewolfRank == 1:
                sqlRank1 = ('UPDATE player_attributes set damage = 3 where player_id =%s')
                cur.execute(sqlRank1, (player_id,))
                return True
            elif werewolfRank == 2:
                sqlRank2Damage = ('UPDATE player_attributes set damage = 5 where player_id =%s')
                cur.execute(sqlRank2Damage, (player_id,))
                sqlRank2HP = ('UPDATE player_attributes set HP = 15 where player_id =%s')
                cur.execute(sqlRank2HP, (player_id,))
                return True
            elif werewolfRank == 3:
                sqlRank3Damage = ('UPDATE player_attributes set damage = 8 where player_id =%s')
                cur.execute(sqlRank3Damage, (player_id,))
                sqlRank3HP = ('UPDATE player_attributes set HP = 20 where player_id =%s')
                cur.execute(sqlRank3HP, (player_id,))
                return True
            conn.commit()
    #add all damage from the inventory
    def add_damage(self, player_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlInventory = ('select damage from inventory join item on inventory.itemid = item.itemid join weapons on weapons.item_id = item.itemid where inventory.player_id =%s')
            cur.execute(sqlInventory,(player_id,))
            inventoryDamage = cur.fetchall()
            damageTotal = 0
            for item in inventoryDamage:
                damageTotal += item[0]
            return damageTotal
    #add all the armor from the inventory
    def add_HP(self, player_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlInventory = ('select armor from inventory join item on inventory.itemid = item.itemid join armor on armor.item_id = item.itemid where inventory.player_id =%s')
            cur.execute(sqlInventory,(player_id,))
            inventoryDamage = cur.fetchall()
            armorTotal = 0
            for item in inventoryDamage:
                armorTotal += item[0]
            return armorTotal
    #get playerid 
    def get_playerid(self, username):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlPlayerid = ('select current_player from gameuser where username=%s')
            cur.execute(sqlPlayerid,(username,))
            playeridreturn = int(cur.fetchone()[0])
            return playeridreturn
    def set_werewolf(self, player_id):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sqlWerewolf =('UPDATE player set is_werewolf = 1 WHERE player_id = %s')
            cur.execute(sqlWerewolf, (player_id,))
    def listPlayerid(self, game_id):
        conn = self.get_db()
        with conn:
            cmd = ('select player_id from player where game_id = %s')
            cur = conn.cursor()
            cur.execute(cmd, (game_id,))
            listPlayers = cur.fetchall()
            shuffle(listPlayers)
        return listPlayers

    def set_random_landmark(self, game_id, minValue, maxValue, radius, num_landmark):
        conn = self.get_db()
        with conn:
            cur = conn.cursor()
            sql = ('INSERT INTO landmark (game_id, lat, lng, radius, type) VALUES (%s,%s,%s,%s,%s)')
                       
            for i in range(num_landmark):
                typeLand = random.randint(0,1)
                if typeLand == 0: #safe_zone
                        latRand = random.uniform(minValue, maxValue)
                        lngRand = random.uniform(minValue, maxValue)
                        cur.execute(sql, (game_id, latRand, lngRand, radius, typeLand,))
                        conn.commit()
                else: #treasure
                        latRand = random.uniform(minValue, maxValue)
                        lngRand = random.uniform(minValue, maxValue)
                        
                        cur.execute(sql, (game_id, random.uniform(minValue, maxValue), random.uniform(minValue, maxValue), radius, typeLand,))
                        conn.commit()
                        
                        sqlItem = ('SELECT COUNT(*) from item')
                        cur.execute(sqlItem)
                        numItem = int(cur.fetchone()[0])
                        randItem = random.randint(1, numItem)
                        
                        sqlLandmarkId = ('select landmark_id from landmark order by landmark_id desc limit 1;')
                        cur.execute(sqlLandmarkId)
                        landMarkid = int(cur.fetchone()[0])
                        
                        sqlTreasure = ('INSERT INTO treasure VALUES (%s,%s,%s)')
                        cur.execute(sqlTreasure, (landMarkid, randItem, random.randint(1,4)))
                        conn.commit()


















            
if __name__ == "__main__":
    dao = WherewolfDao('wherewolf','kchow95','4zzvanou')

    # dao.clear_tables()
    # try:
    #     dao.create_user('rfdickerson', 'awesome', 'Robert', 'Dickerson')
    #     dao.create_user('oliver','furry','Oliver','Cat')
    #     dao.create_user('vanhelsing', 'van', 'Van', 'Helsing')
    #     print 'Created a new player!'
    # except UserAlreadyExistsException as e:
    #     print e
    # except Exception:
    #     print 'General error happened'
        
    # username = 'rfdickerson'
    # correct_pass = 'awesome'
    # incorrect_pass = 'scaley'
    # print 'Logging in {} with {}'.format(username, correct_pass)
    # print 'Result: {} '.format( dao.check_password(username, correct_pass ))
    
    # print 'Logging in {} with {}'.format(username, incorrect_pass)
    # print 'Result: {} '.format( dao.check_password(username, incorrect_pass ))

    # game_id = dao.create_game('rfdickerson', 'TheGame')
    # # dao.create_game('oliver', 'AnotherGame')
    
    # dao.join_game('oliver', game_id)
    # dao.join_game('rfdickerson', game_id)
    # dao.join_game('vanhelsing', game_id)

    # print "Adding some items..."
    # dao.add_item('rfdickerson', 'Silver Knife')
    # dao.add_item('rfdickerson', 'Blunderbuss')
    # dao.add_item('rfdickerson', 'Blunderbuss')
    # dao.add_item('rfdickerson', 'Blunderbuss')
    # dao.add_item('oliver', 'Blunderbuss')
    # dao.remove_item('rfdickerson', 'Blunderbuss')

    # print
    # print 'rfdickerson items'
    # print '--------------------------------'
    # items = dao.get_items("rfdickerson")
    # for item in items:
    #     print item["name"] + "\t" + str(item["quantity"])
    # print

    # # location stuff
    # dao.set_location('rfdickerson', 30.202, 97.702)
    # dao.set_location('oliver', 30.201, 97.701)
    # dao.set_location('vanhelsing', 30.2, 97.7) 
    # loc = dao.get_location('rfdickerson')
    # loc2 = dao.get_location('oliver')
    # print "rfdickerson at {}, {}".format(loc["lat"], loc["lng"]) 
    # print "oliver at {}, {}".format(loc2["lat"], loc2["lng"]) 

    # dao.award_achievement('rfdickerson', 'Children of the moon')
    # dao.award_achievement('rfdickerson', 'A hairy situation')
    # achievements = dao.get_achievements("rfdickerson")

    # print
    # print 'rfdickerson\'s achievements'
    # print '--------------------------------'
    # for a in achievements:
    #     print "{} ({}) - {}".format(a["name"],a["description"],a["created_at"].strftime('%a, %H:%M'))
    # print
    
    # nearby = dao.get_alive_nearby('rfdickerson', game_id, 700000)
    # print ('Nearby players: ')
    # for p in nearby:
    #     print "{} is {} meters away".format(p["player_id"],p["distance"])

    # dao.vote(game_id, 'rfdickerson', 'oliver')
    # dao.vote(game_id, 'oliver', 'vanhelsing')
    # dao.vote(game_id, 'vanhelsing', 'oliver')
    # print 'Players in game 1 are'
    # print dao.get_players(1)
    # dao.set_werewolf('rfdickerson')
    # print dao.get_playerid('oliver')
    #dao.leave_game('michael', 1)
    print dao.is_game_over_w(1)
    print dao.get_current_ballot(1)

    #dao.set_dead('pam')
    #dao.set_dead('andy')
    # print dao.get_userid('rfdickerson')
