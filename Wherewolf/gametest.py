import requests
import json
import time 


hostname = 'http://wherewolf-lb-1339166004.us-west-2.elb.amazonaws.com'
#http://localhost:5000
# user = 'rfdickerson'
# password = 'awesome'
game_id = 0

rest_prefix ="/v1"


''' Important functions
create a game
leave a game
update game state with location
cast a vote
'''

def create_user(username, password, firstname, lastname):
    payload = {'username': username, 'password': password, 'firstname': firstname, 'lastname': lastname}
    url = "{}{}".format(hostname, "/register")
    r = requests.post(url, data=payload)

    response = r.json()
    print response["status"]
    print response["username"]

def create_game(username, password, game_name, description):
    payload = {'game_name': game_name, 'description': description}
    url = "{}{}{}".format(hostname, rest_prefix, "/game")
    print 'sending {} to {}'.format(payload, url)
    r = requests.post(url, auth=(username, password), data=payload)

    response = r.json()
    #rjson = json.loads(response)
    #print rjson["status"]
    print response["status"]
    return response["results"]["game_id"]
    
def leave_game(username, password, game_id):
    payload = {'game_id': game_id}
    r = requests.post(hostname + rest_prefix + "/game/" + str(game_id) + "/leave", auth=(username, password), data=payload)
    response = r.json()

    print response["status"]
    return response["status"]

def join_game(username, password, game_id):
    print 'Joining game id {}'.format(game_id)
    payload = {'game_id': game_id}
    url = "{}{}/game/{}/lobby".format(hostname, rest_prefix, game_id)
    r = requests.put(url, auth=(username, password), data=payload)
    r = r.json()
    print r 
    return r
 

def delete_game(username, password, game_id):
    payload = {'game_id': game_id}
    r = requests.delete(hostname + rest_prefix + "/game/" + str(game_id), auth=(username, password), data=payload)
    response = r.json()

    print response["status"]
    return response["status"]

def update_game(username, password, game_id, lat, lng):
    """ reports to the game your current location, and the game 
    returns to you a list of players nearby """

    payload = {'lat': lat, 'lng': lng}
    url = "{}{}/game/{}".format(hostname, rest_prefix, game_id)
    r = requests.put(url, auth=(username, password), data=payload)
    response = r.json()

    print response
def update_location(username, password, game_id, lat, lng):
    """ reports to the game your current location, and the game 
    returns to you a list of players nearby """

    payload = {'game_id': game_id, 'lat': lat, 'lng': lng}
    url = "{}{}/game/{}".format(hostname, rest_prefix, game_id)
    r = requests.put(url, auth=(username, password), data=payload)
    response = r.json()

    print response
    return response

def set_gametime(game_id, time):
    payload = {'game_id': game_id, 'time': time}
    r = requests.post(hostname + rest_prefix + "/game/" + str(game_id) + "/time", data = payload)
    response = r.json()

    print response


def game_info(username, password, game_id):
    ''' returns all the players, the time of day, and other options for the game '''
    payload = {'game_id': game_id}
    url = "{}{}/game/{}".format(hostname, rest_prefix, game_id)
    r = requests.get(url, auth=(username, password),data=payload)
    response = r.json()
    print response

def cast_vote(username, password, game_id, player_id):
    payload = {'player_id': player_id, 'username': username, 'game_id': game_id}
    
    r = requests.post(hostname + rest_prefix + "/game/" + str(game_id) + "/ballot", auth=(username, password), data=payload)
    response = r.json()

    print response
def attack(game_id, player_username, target_username):
    payload = {'player_username': player_username, 'game_id': game_id, 'target_username': target_username}

    r = requests.post(hostname + rest_prefix + "/game/" + str(game_id) + "/attack", data =payload)
    response = r.json()
    print response
    return response
def set_game_state(game_state):
    payload = {'game_id': game_id, 'game_state': 'night'}
    r = requests.post(hostname + rest_prefix + "/game/admin")
    r = r.json()
    print response

def join_game(username, password, game_id):
    print 'Joining game id {}'.format(game_id)
    payload = {'game_id': game_id}
    r = requests.post(hostname + rest_prefix + "/game/" + str(game_id) + "/lobby" , auth=(username, password), data = payload)
    r = r.json()
    print r

def get_games(username, password):
    r = requests.get(hostname + rest_prefix + "/game")
    r = r.json()
    return r["results"]
def ballot_info(username, password, game_id):
    ''' returns ballet information in the game '''
    payload = {'game_id': game_id}
    url = "{}{}/game/{}/ballot".format(hostname, rest_prefix, game_id)
    r = requests.get(url, auth=(username, password),data=payload)
    response = r.json()
    print response
def start_game(game_id):
    payload = {'game_id': game_id}
    r = requests.post(hostname + rest_prefix + "/game/" + str(game_id), data = payload)
    response = r.json()
    return response
def create_users():
    create_user('michael', 'paper', 'Michael', 'Scott')
    create_user('dwight', 'paper', 'Dwight', 'Schrute')
    create_user('jim', 'paper', 'Jim', 'Halpert')
    create_user('pam', 'paper', 'Pam', 'Beesly')
    create_user('ryan', 'paper', 'Ryan', 'Howard')
    create_user('andy', 'paper', 'Andy', 'Bernard')
    create_user('angela', 'paper', 'Angela', 'Martin')
    create_user('toby', 'paper', 'Toby', 'Flenderson')

def werewolf_winning_game():
    game_id = create_game('michael', 'paper', 'NightHunt', 'A test for werewolf winning')
    print game_id
    
    print "-----------joining game-----------"

    join_game('dwight', 'paper', game_id)
    join_game('jim', 'paper', game_id)
    join_game('pam', 'paper', game_id)
    join_game('ryan', 'paper', game_id)
    join_game('andy', 'paper', game_id)
    join_game('angela', 'paper', game_id)
    join_game('toby', 'paper', game_id)
    start_game(game_id)

    print "-----------Daytime-----------"
    set_gametime(1,time.strftime('2014-01-22 %09:00:00'))

    print "-----------Night-----------" #attacks will fail if they aren't a werewolf
    set_gametime(1,time.strftime('2014-01-22 %19:13:04'))
    attack(game_id, 'dwight', 'toby')
    attack(game_id, 'ryan', 'andy')
    attack(game_id, 'pam', 'ryan')
    attack(game_id, 'andy', 'pam')
    attack(game_id, 'angela', 'jim')
    attack(game_id, 'toby', 'dwight')

    print "---------Daytime2----------"
    cast_vote('dwight','paper', 1, 6)
    cast_vote('jim','paper', 1, 6)
    cast_vote('toby','paper', 1, 6)

    ballot_info('dwight', 'paper', 1)

    update_location('michael', 'paper', 2, 3, 4) 
    game_info('michael', 'paper', 1)

    
    
    leave_game('michael', 'paper', 1)
def check_server():
    url = "http://127.0.0.1:5000/"
    r = requests.get(url)
    print r.text

def check_db():
    url = hostname + "/check_db"
    r = requests.get(url)
    print r.text

if __name__ == "__main__":
    # check_server()
    #check_db()
    #join_game('michael', 'paper', 2)
    #delete_game('michael', 'paper', 1)
    #cast_vote('rfdickerson','awesome', 2, 5)
    #start_game(1)
    create_users()
    werewolf_winning_game()
    #cast_vote('ryan', 'paper', 1 , 3)
    #ballot_info('dwight', 'paper', 1)
   #game_info('michael', 'paper', 1)
    #leave_game('dwight', 'paper', 1)
    #game_info('michael', 'paper', 1)

    #attack(1, 'pam', 'jim')
   # create_game('rfdickerson', 'awesome', 'NightHunt', 'A game in Austin')
   # game_info('rfdickerson', 'awesome', 22)
   # leave_game('rfdickerson', 'awesome', 302)