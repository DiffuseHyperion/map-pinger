import requests
from flask import Flask, render_template, jsonify
from mcstatus import JavaServer

app = Flask(__name__)
server_url = "mc.diffusehyperion.me"
map_url = "https://map.diffusehyperion.me"

def name_list_to_string(name_list):
    if len(name_list) <= 0:
        return "Nobody"
    elif len(name_list) == 1:
        return name_list[0]
    else:
        res = ""
        for index, name in enumerate(name_list):
            if index <= 0:
                res += name
            elif index != (len(name_list) - 1):
                res += ", "
                res += name
            else:
                res += " and "
            res += name
    return res

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/info.html')
def info():
    return render_template("info.html")

@app.route('/ajax/map')
def ping_map():
    map_status = ""
    map_status_class = ""
    try:
        response = requests.get(map_url, timeout=3)
        response.raise_for_status()
        map_status = "Online!"
        map_status_class = "success"
    except requests.exceptions.HTTPError as err:
        code = int(str(err)[:3])
        map_status = ""
        if code == 502: # Main Server offline
            map_status = "Offline..."
        else:
            map_status = "Catastrophically Offline!!!"
        map_status_class = "error"
    except requests.exceptions.SSLError or requests.exceptions.ConnectionError or requests.exceptions.ConnectionTimeout:
        print("SSLError")
        map_status = "Catastrophically Offline!!!"
        map_status_class = "error"
    return jsonify(map_status=map_status, map_status_class=map_status_class)

@app.route('/ajax/server')
def ping_server():
    server_status = ""
    server_status_class = ""
    try:
        server = JavaServer.lookup(server_url, timeout=3)
        server.ping()
        server_status = "Online!"
        server_status_class = "success"
    except ConnectionRefusedError: # server is off
        server_status = "Offline..."
        server_status_class = "error"
    return jsonify(server_status=server_status, server_status_class=server_status_class)

@app.route('/ajax/stats')
def server_stats():
    server = JavaServer.lookup(server_url)
    status = server.status()
    server_player_list = []
    for player in status.players.sample:
        server_player_list.append(player.name)
    
    server_player_string = name_list_to_string(server_player_list)
    server_ping = server.ping()
    return jsonify(server_player_string=server_player_string, server_ping=server_ping)

if __name__ == "__main__":
    app.run()
