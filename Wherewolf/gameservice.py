from flask import Flask, request, jsonify
import psycopg2
app = Flask(__name__)
from wherewolfdao import WherewolfDao
from random import randrange
import random
from datetime import datetime
db = WherewolfDao()

@app.route('/healthcheck')
def health_check():
    return "healthy"

def get_db(databasename='wherewolf', 
        username='kchow95',
        password='4zzvanou'):
    return psycopg2.connect(database= databasename,
             user=username, password=password)

@app.route("/check_db")
def check_db():
    conn =db.get_db()
    if conn:
        return "working"
    else:
        return "fail"

@app.route("/")
def hello():
    return "Hello World!"
@app.route('/v1/check_password', methods=["GET"] )
def checking_password():
    auth = request.authorization
    username = auth.username
    password = auth.password
    print password
    print 'checking password for {}'.format(username)
    
    
    conn = db.get_db()
    response = {}
    with conn:
        sql = ('select password from gameuser '
               'where username=%s')
        cur = conn.cursor()
        cur.execute(sql, (username, ))
        dbpass = cur.fetchone()[0]
        print '----------------{}'.format(dbpass)
        if dbpass == password: 
            response["status"] = "success"
            print "success"
        else:
            response["status"] = "failure"
            print "fail"
        return jsonify(response)         

def check_password(username, password):
    print 'checking password for {}'.format(username)
    conn = db.get_db()
    response = {}
    with conn:
        sql = ('select password from gameuser '
               'where username=%s')
        cur = conn.cursor()
        cur.execute(sql, (username, ))
        dbpass = cur.fetchone()[0]
        print '----------------{}'.format(dbpass)
        dbpass = db.check_password(username, password)
        return dbpass == password

@app.route('/register', methods=["POST"])
def create_user():
    print "----creating user----"
    auth = request.authorization
    conn = db.get_db()
    firstname = request.form['firstname']
    print 'hi'
    lastname = request.form['lastname']
    print 'bye'
    username = auth.username
    password = auth.password
    print 'no'
    
    #db.create_user(username, password, firstname, lastname)

    response = {}
    response["status"] = "failure"
    
    if db.create_user(username, password, firstname, lastname) != -1:
        print 'created a user called {}'.format(username)
        response["status"] = "success"
        response["username"] = username
<<<<<<< HEAD
        db.join_game(username, 1)
=======
        
>>>>>>> b0f92809f4a8d77d561cf2786f65857a08b24f26
        # MIME application/json
    
    return jsonify(response)


@app.route('/v1/get_games', methods=["GET"])
def get_games():
    #connect to database
    conn = db.get_db()
    
    #default response
    response = {}
    response["status"] = "failure"
    
    with conn:
        cur = conn.cursor()
        response["games"]=db.get_games()
        response["number_of_games"]=db.count_games()
        response["status"]="success"
        
    return jsonify(response)


@app.route('/v1/game', methods=["POST"])
def create_game():
    #connect to database
    conn = db.get_db()

    #request information
    game_name = request.form["game_name"]
    description = request.form["description"]

    auth = request.authorization
    username = auth.username
    password = auth.password
    print "hi"
    #default response
    response = {}
    response["status"] = "failure"
    response["game_id"] = None
    response["results"] = None
    print password
    #get userid
    userid = db.get_userid(username)
    print password
    #print(userid)
    print username
    print check_password(username, password)
    #check if password works
    with conn:
        cur = conn.cursor()
       #check if admin_id already exists with userid
        cur.execute('SELECT admin_id from game where admin_id=%s', (userid,))
        if cur.fetchone() == None:           
            #create game in database
            insertsql = ('insert into game (admin_id, name, description) values (%s, %s, %s)')
            game_id = db.create_game(username, game_name, description)
            db.join_game(username, game_id)

            #set status
            response["status"] = "success"
                
            #get game id
            cur.execute('SELECT game_id from game where admin_id=%s', (userid,))
            response["game_id"]=cur.fetchone()[0]
            response["results"]={"game_id":response["game_id"]}

    return jsonify(response)
@app.route('/v1/game/<int:game_id>', methods=["DELETE"])
def delete_game(game_id):
    #connect to database
    conn = db.get_db()

    print("connected")
    
    #request information
    game_id = request.form["game_id"]
    response = {}
    response["status"] = "failure"
    auth = request.authorization
    username = auth.username
    password = auth.password

    #default response

    #get userid
    userid = db.get_userid(username)
    if check_password(username,password):
        gameid = db.check_if_game_admin(userid)
        if (gameid[0] != None and int(game_id) == gameid[0]):
            with conn:
                db.delete_game(gameid)

                #set status
                response["status"] = "success"

    return jsonify(response)

@app.route('/v1/game/<int:game_id>/lobby', methods=["POST"])
def join_game(game_id):
    #connect to database
    conn = db.get_db()
    auth = request.authorization
    username = auth.username
    password = auth.password
    game_id = request.form["game_id"]
    response = {}
    response["status"] = "failure"
    userid = db.get_userid(username)
    
    #check if password works
        #check if user already is in a game
    print(db.check_if_in_game(userid))        
    if db.check_if_in_game(userid):
        with conn:
            cur = conn.cursor()
                
            #check if game in lobby mode
            lobby = db.check_lobby_mode(game_id)
            if lobby==0:           
                #join the game as a player
                db.join_game(username, game_id)
                #set status
                response["status"] = "success"
                
    return jsonify(response)
@app.route('/v1/game/<int:game_id>/leave', methods =["POST"])
def leave_game(game_id):
    #connect to database
    print "hi"
    conn = db.get_db()
    auth = request.authorization
    username = auth.username
    password = auth.password
    game_id = request.form["game_id"]
    response = {}
    response["status"] = "failure"
    userid = db.get_userid(username)
    

    print(db.check_if_in_game(userid))
        
<<<<<<< HEAD
    if db.check_if_in_game(userid):
=======
    if db.check_if_in_game(userid)==False:
>>>>>>> b0f92809f4a8d77d561cf2786f65857a08b24f26
        with conn:

                db.leave_game(username, game_id)
                    
                #set status
                response["status"] = "success"
                
    return jsonify(response)
@app.route('/v1/game/<int:game_id>', methods=["POST"])
def update_location(game_id):
    #default 
    print 'hi'
    conn = db.get_db()
    auth = request.authorization
    
    password = auth.password
    username = auth.username
    print 'hello'
    lat = request.form["lat"]
    lng = request.form["lng"]
    print lat
    game_id = request.form["game_id"]
    print 'here'
    response = {}
    response["status"] = "success"
    
    print username
    print password
    print game_id
    #get userid
    db.set_location(username, float(str(lat)), float(str(lng)))
    cur = conn.cursor()
    cur.execute('SELECT * from gametime where game_id=%s', (game_id))
    if cur.fetchone() == None:
<<<<<<< HEAD
        sql = ('INSERT INTO gametime (game_id) VALUES (%s)')
        cur.execute(sql, (game_id,))
=======
        curTime2 = datetime.now().time()
        sql = ('INSERT INTO gametime (time, game_id) VALUES (%s, %s)')
        cur.execute(sql, (curTime2, game_id,))
>>>>>>> b0f92809f4a8d77d561cf2786f65857a08b24f26
        conn.commit()
        response["status"] = "success"
    else:
        curTime = datetime.now().time()
        sql2 = ('UPDATE gametime set time = %s where game_id = %s')
        cur.execute(sql2, (curTime, game_id))

    cur.execute('SELECT time from gametime where game_id=%s', (game_id))
    response["results"] = str(cur.fetchone()[0])
    print response["results"]
       #check if password works
    if check_password(username,password):

        with conn:
            cur = conn.cursor()
            
            #set location
            db.set_location(username, float(str(lat)), float(str(lng)))

            #get whoever is nearby
           
                 
            #successful
            response["status"] = "success"
            
    return jsonify(response)
    
@app.route('/v1/game/<int:game_id>/time', methods=["POST"])
def update_gametime(game_id):
    conn = db.get_db()
    game_id = request.form["game_id"]
    time = request.form["time"]
    response = {}
    cur = conn.cursor()
    cur.execute('SELECT * from gametime where game_id=%s', (game_id))
    if cur.fetchone() == None:
        sql = ('INSERT INTO gametime VALUES (%s, %s)')
        cur.execute(sql, (game_id, time,))
        conn.commit()
        response["status"] = "success"
    else:
        sql = ('UPDATE gametime set time =%s where game_id =%s')
        cur.execute(sql, (time, game_id,))
        conn.commit()
        response["status"] = "success"

    return jsonify(response)
@app.route('/v1/game/<int:game_id>', methods=["GET"])
def game_info(game_id):
    #connect to database
    conn = db.get_db()

    #request information
    game_id = request.form["game_id"]

    
    #username/password
    auth = request.authorization
    username = auth.username
    password = auth.password
   
    #default response
    response = {}
    response["status"] = "failure"
    #check if password works
    if check_password(username,password):
        response["game_info"] = db.game_info(game_id)
        response["status"] = "success"      
  
    return jsonify(response)
@app.route('/v1/game/<int:game_id>', methods=["POST"])
def start_game(game_id):
    conn = db.get_db()
    cur = conn.cursor()
    game_id = request.form["game_id"]
    playeramount = db.count_players(int(game_id))
    listPlayers = db.listPlayerid(game_id)
    counter = 0
    while(counter < playeramount/3):
        db.set_werewolf((listPlayers[counter]))
        counter+=1
    response = {}
    db.set_game_status(game_id, 1)
    response["status"] = "begin"
    return jsonify(response)
@app.route('/v1/game/<int:game_id>', methods = ["POST"])

@app.route('/v1/game/<int:game_id>/landmark', methods =["POST"])
def set_landmark(game_id):
    conn = db.get_db()
    
    response = {}
    response["status"] = 'failure'
    response["num_landmark"] = '0'
    
    #request information
    game_id = int(request.form["game_id"])
    minValue = float(request.form["minValue"])
    maxValue = float(request.form["maxValue"])
    radius = int(request.form["radius"])
    num_landmark = int(request.form["num_landmark"])
    
    db.set_random_landmark(game_id, minValue, maxValue, radius, num_landmark)

    response["status"] = 'success'
    response["num_landmark"] = num_landmark
    
    return jsonify(response)



@app.route('/v1/game/<int:game_id>/ballot', methods=["POST"])
def cast_ballot(game_id):
    conn = db.get_db()
    game_id = request.form["game_id"]
    game_id= int(game_id)
    print game_id
    player_id = request.form["player_id"]
    playertargetint = int(player_id)
    auth = request.authorization
    username = auth.username
    password = auth.password
    response = {}
    print username
    cur = conn.cursor()
    #prepare sql statements 
    idsql = ('SELECT current_player from gameuser where username =%s')
    cur.execute(idsql, (username,))
    playercast = cur.fetchone()[0]
    print playercast
    response["status"] = "failure"
    selectsql = ('SELECT game_id from player where player_id =%s')
    cur.execute(selectsql, (playercast,))
    gamein = cur.fetchone()[0]
    #gamein is checking to make sure that the 
    playerint = int(playercast)
    #
    print gamein;
    #checking the password 
    if check_password(username, password):
        if game_id == gamein:
            db.vote(game_id, playerint, playertargetint)
            response["status"] = "success"

    return jsonify(response)
@app.route('/v1/game/<int:game_id>/ballot', methods=["GET"])
def get_ballot_info(game_id):
    #connect to database
    conn = db.get_db()
    #get all the parameters
    auth = request.authorization
    username = auth.username
    password = auth.password
    game_id = request.form["game_id"]
    response = {}
    response["status"] = "failure"
    
    #get userid
    user_id = db.get_userid(username)

    if db.check_if_in_game(user_id) == False:
        #validate user
        if check_password(username,password):
            #how many votes per person
            response["results"] = db.get_current_ballot(str(game_id))
            print(db.get_current_ballot(str(game_id)))
            response["status"] = "success"      

    return jsonify(response)
@app.route('/v1/game/<int:game_id>/attack', methods=["POST"])
def attack(game_id):
    conn = db.get_db()
    #get all the parameters
    game_id = request.form["game_id"]
    player_username = request.form["player_username"]
    target_username = request.form["target_username"]
    #change to player_id
    player_id = db.get_playerid(player_username)
    target_id = db.get_playerid(target_username)
    response = {}
    if(db.set_baseWerewolf(player_username) == False or db.set_baseWerewolf(target_username) == True):
        response["status"] = 'failed' 
    #get all the damage
    else:
        hpAttacker = db.get_HP(player_id) + db.add_HP(player_id)
        hpTarget = db.get_HP(target_id) +db.add_HP(target_id)
        damageAttacker = db.get_damage(player_id) + db.add_damage(player_id)
        damageTarget = db.get_damage(target_id) + db.add_damage(target_id)
        #set all the bools
        someoneDead = False 
        attackerDead = False
        targetDead = False
        #run until someone dies
        while someoneDead == False:
            #attack is random
            hpTarget -= random.randint(0,damageAttacker)
            print hpTarget
            #if target goes below 0, then get out
            if hpTarget < 0:
                someoneDead = True
                targetDead = True
                break 
            hpAttacker -= random.randrange(0,damageTarget)
            print hpAttacker
            #if attacker goes below 0, get out 
            if hpAttacker <0:
                someoneDead = True
                attackerDead = True
        #check the winners and set people dead
        if attackerDead:
            response["winner"] = target_username
            response ["status"] = 'success'
            db.set_dead(player_username)
        else:
            response["winner"] = player_username
            response ["status"] = 'success'
            db.set_dead(target_username)
    return jsonify(response)









    
if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)
