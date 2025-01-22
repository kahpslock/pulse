from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import os
import time
from datetime import datetime
import json
import uuid
import requests
import collections
import threading
import random
import mysql.connector
import shortuuid
from datetime import datetime
global unitlist
global numdebug
global sql
global sqlcur
sql = mysql.connector.connect(
host="REDACTED",
user="REDACTED",
password="REDACTED",
database="REDACTED"
)
sqlcur = sql.cursor(buffered=True)
global sqlcommandList
global cadUsersList
global cadCommunitiesList
global cadCivRecordsList
global cadCiviliansList
global cadCivList
global cadCarsList
global bannediplist
global authuserslist
global usersList9m
sqlcommandList = []
cadUsersList = []
cadCommunitiesList = []
cadCivRecordsList = []
cadCiviliansList = []
cadCivList = []
cadCarsList = []
numdebug = 0
unitlist = []
bannediplist = []
authuserslist = []
usersList9m = []
global errorlist
errorlist = []
def accesslog(a):
    unixtime = int(time.time())
    r = requests.post("https://discord.com/api/webhooks/1120160518011883601/9wJ7GOGy13Bha_lOCHTF6fSyhKuiF7uVIJssPTrY0L1NJ4HCf3ty8jwPzvQQQbAH---J", json={"embeds": [{"title": "Access Attempt", "description": "IP: " + a + "\n\nDate/Time: <t:" + str(unixtime) + ">,<t:" + str(unixtime) + ":R>", "color": 16711680}]})
def checkbanned(a):
    for i in bannediplist:
        if i['ip'] == a:
            errorid = shortuuid.uuid()
            unixtime = int(time.time())
            reason = i['reason']
            errorlist.append({'id': errorid, 'ip': a, 'time': unixtime})
            r = requests.post("https://discord.com/api/webhooks/1120139841393405972/DOIv_E0GkXz_sOvPBF0yXz-w1wdIbY2B4lt-ETJDQ-bQcc7V01fY9yjX-6ZKkdQV2ooi", json={"embeds": [{"title": "Blacklisted Access Attempt", "description": "Error ID: " + errorid + "\n\nIP: " + a + "\n\nBlacklist Reason: " + reason + "\n\nDate/Time: <t:" + str(unixtime) + ">,<t:" + str(unixtime) + ":R>", "color": 16711680}]})

            return errorid

    return False
app = Flask(__name__)
CORS(app)
def mysqlup():
    sqlreconnecting = False
    while True:
        sqllive = sql.is_connected()
        if sqllive == False:
            print("Reconnecting to Mysql")
            sqlreconnecting = True
            try:
                sql.reconnect()
            except:
                pass
        else:
            if sqlreconnecting == True:
                print("Successfully Reconnected")
                sqlreconnecting = False
            else:
                for i in sqlcommandList:
                    sqlcur.execute(i)
                    sql.commit()
                    sqlcommandList.remove(i)
def fxservercheckupdates():
    global fxserverversion
    global fxserverlink
    print("FXServer Update Checker Started")
    while True:
        try:
            r = requests.get("https://changelogs-live.fivem.net/api/changelog/versions/linux/server")
            fxserverlink2 = json.loads(r.text)['latest_download']
            fxserverversion2 = int(json.loads(r.text)['latest'])
            if isinstance(fxserverversion2, int) == False:
                print("FXServer Version Check Failed")
                pass
            if int(fxserverversion) < int(fxserverversion2):
                print("New FXServer Version: " + str(fxserverversion2) + " Download Link: " + fxserverlink2)
                sqlcommandList.append("UPDATE fxserverversion SET version = '" + str(fxserverversion2) + "', link = '" + fxserverlink2 + "'")
                fxserverversion = fxserverversion2
                fxserverlink = fxserverlink2
                url = "https://discord.com/api/webhooks/1148454852809203742/P2UL28ry29bxJ1iFtLa-CW2o-x5pqfNwmKLj89yxSvkD32IxEQsUFVh8n0yviwiAFiml"
                contentsend = "New FXServer Version: " + str(fxserverversion2) + '\nTo update your server automatically, go to your server on https://panel.9mhosting.com, then go to the settings.\nClick the "Reinstall Server" Button, and it *should* Update.\nIf your server does not update automatically, let us know.' + "\n\nManual Download Link: " + fxserverlink2 + "\n\nI would include a changelog, but CFX quit doing that? :/"
                data = {
                    "content": contentsend,
                    "avatar_url": "https://knowtechie.com/wp-content/uploads/2021/03/dogecoin-meme-1000x600.jpg",
                    "username": "FXServer Update Notifs"
                }
                r = requests.post(url, json=data)
            time.sleep(60)
        except:
            pass
def mysqlload():
    global cadUsersList
    global cadCommunitiesList
    global cadCivRecordsList
    global cadCiviliansList
    global cadCarsList
    global bannediplist
    global authuserslist
    global fxserverversion
    global fxserverlink
    sqlcur.execute("SELECT * FROM fxserverversion")
    for row in sqlcur:
        fxserverversion = int(row[0])
        fxserverlink = row[1]
    sqlcur.execute("SELECT * FROM authbannedips")
    for row in sqlcur:
        bannediplist.append({'ip': row[0], 'reason': row[1]})
    sqlcur.execute("SELECT * FROM authusers")
    for row in sqlcur:
        authuserslist.append({'username': row[0], 'password': row[1]})
    sqlcur.execute("Select * FROM cadUsers")
    sqlres = sqlcur.fetchall()
    for row in sqlres:
        username = row[0]
        password = row[1]
        token = row[2]
        communities = row[3]
        cadUsersList.append({"username": username, "password": password, "token": token, "communities": communities})
    print("loaded cadUsersList")
    sqlcur.execute("Select * FROM cadCommunities")
    sqlres = sqlcur.fetchall()
    for row in sqlres:
        commname = row[0]
        comkey = row[1]
        owner = row[2]
        num911 = row[3]
        imageurl = row[4]
        cadCommunitiesList.append({"commname": commname, "comkey": comkey, "owner": owner, "911num": num911, "imageurl": imageurl})
    print("loaded cadCommunitiesList")
    sqlcur.execute("Select * FROM cadCivilians")
    sqlres = sqlcur.fetchall()
    for row in sqlres:
        firstname = row[0]
        lastname = row[1]
        dob = row[2]
        social = row[3]
        gender = row[4]
        race = row[5]
        haircolor = row[6]
        build = row[7]
        height = row[8]
        communityid = row[9]
        phone = row[10]
        owner = row[11]
        warrant = row[12]
        occupation = row[13]
        address = row[14]
        cadCiviliansList.append({"firstname": firstname, "lastname": lastname, "dob": dob, "social": social, "gender": gender, "race": race, "haircolor": haircolor, "build": build, "height": height, "communityid": communityid, "phone": phone, "owner": owner, "warrant": warrant, "occupation": occupation, "address": address})                                 
    print("loaded cadCiviliansList")
    sqlcur.execute("Select * FROM cadCars")
    sqlres = sqlcur.fetchall()
    for row in sqlres:
        make = row[0]
        model = row[1]
        color = row[2]
        lplate = row[3]
        social = row[4]
        communityid = row[5]
        stolen = row[6]
        cadCarsList.append({"make": make, "model": model, "color": color, "lplate": lplate, "social": social, "communityid": communityid, "stolen": stolen})
    print("loaded cadCarsList")
    sqlcur.execute("Select * FROM cadCivRecords")
    sqlres = sqlcur.fetchall()
    for row in sqlres:
        author = row[0]
        social = row[1]
        firstname = row[2]
        lastname = row[3]
        communityid = row[4]
        recdate = row[5]
        type = row[6]
        details = row[7]
        recid = row[8]
        cadCivRecordsList.append({"author": author, "social": social, "firstname": firstname, "lastname": lastname, "communityid": communityid, "recdate": recdate, "type": type, "details": details, "recid": recid})
    print("loaded cadCivRecordsList")
    sqlcur.execute("Select * FROM 9musers")
    sqlres = sqlcur.fetchall()
    for row in sqlres:
        username = row[0]
        password = row[1]
        token = row[2]
        email = row[3]
        emailverified = row[4]
        discordid = row[5]
        customerid = row[6]
        avatarlink = row[7]
        usersList9m.append({"username": username, "password": password, "token": token, "email": email, "emailverified": emailverified, "discordid": discordid, "customerid": customerid, "avatarlink": avatarlink})
    print("loaded usersList9m")
    supermp1 = threading.Thread(target=mysqlup)
    supermp1.daemon = True
    supermp1.start()
    supermp2 = threading.Thread(target=fxservercheckupdates)
    supermp2.daemon = True
    supermp2.start()
mysqlload()
@app.route('/debug', methods=['POST', 'GET'])
def debugreq():
    url = "https://discord.com/api/webhooks/1064596341533200484/ziFg9PXCJWG0EE1dSMFDv9OQVNw5O03vw8UzapbakjxYQg1qZKiKM1YIgstU058nwRnM"
    global numdebug
    numdebug = numdebug + 1
    contentsend = "Request #" + str(numdebug) + "\n" + str(request.headers) + "\n" + str(request.data)
    data = {
        "content": contentsend,
        "avatar_url": "https://knowtechie.com/wp-content/uploads/2021/03/dogecoin-meme-1000x600.jpg",
        "username": "API Debug Logs"
    }
    r = requests.post(url, json=data)
    return("Received Debug Request")





#9M Hosting Stuff
@app.route('/latestfxlink', methods=['GET'])
def latestfxlink():
    return(fxserverlink)


@app.route('/hosting9m/', methods=['GET'])
def hosting9m():
    if request.method == 'GET':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        errorid = checkbanned(ip)
        if errorid != False:
            return render_template("banned.html", bannedip = ip, errorid = errorid)
        else:
            accesslog(ip)
            return render_template("index9m.html", ip = ip)
@app.route('/hosting9m/gameservers', methods=['POST', 'GET'])
def hosting9mlogin():
    if request.method == 'GET':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        errorid = checkbanned(ip)
        if errorid != False:
            return render_template("banned.html", bannedip = ip, errorid = errorid)
        else:
            accesslog(ip)
            return render_template("gameservers9m.html", ip = ip)
@app.route('/hosting9m/login', methods=['POST', 'GET'])
def login9m():
    if request.method == 'GET':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        errorid = checkbanned(ip)
        if errorid != False:
            return render_template("banned.html", bannedip = ip, errorid = errorid)
        else:
            accesslog(ip)
            return render_template("login9m.html", ip = ip)
@app.route('/hosting9m/account', methods=['POST', 'GET'])
def account9m():
    if request.method == 'GET':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        errorid = checkbanned(ip)
        if errorid != False:
            return render_template("banned.html", bannedip = ip, errorid = errorid)
        else:
            accesslog(ip)
            return render_template("account9m.html", ip = ip)
@app.route('/hosting9m/loginuser', methods=['GET'])
def loginuser9m():
    found = False
    username = request.args.get('user')
    password = request.args.get('pass')
    global usersList9m
    for i in usersList9m:
        if i['username'] == username:
            if i['password'] == password:
                token = (i['token'])
                found = True
    if found == True:
        return(token)
    else:
        return("403")
@app.route('/hosting9m/registeruser', methods=['GET'])
def registeruser9m():
    found = False
    regusername = request.args.get('user')
    regpassword = request.args.get('pass')
    for i in usersList9m:
        if i['username'] == regusername:
            return("403")
        else:
            found = False
    if found == False:
        token1 = str(uuid.uuid4())
        token2 = str(uuid.uuid4())
        token3 = str(uuid.uuid4())
        customerid = shortuuid.uuid()
        print(customerid)
        token = (token1 + token2 + token3)
        usersList9m.append({"username": regusername, "password": regpassword, "token": token, "email": "", "emailverified": "false", "discordid": "", "customerid": customerid})
        sqlcommandList.append("INSERT IGNORE INTO 9musers(username, password, token, customerid) VALUES ('" + regusername + "', '" + regpassword + "', '" + token + "', '" + customerid + "')")
        return(token)
@app.route('/hosting9m/userinfo', methods=['GET'])
def userinfo9m():
    found = False
    token = request.args.get('usertoken')
    global usersList9m
    for i in usersList9m:
        if i['token'] == token:
            username = (i['username'])
            email = (i['email'])
            emailverified = (i['emailverified'])
            discordid = (i['discordid'])
            customerid = (i['customerid'])
            avatarlink = (i['avatarlink'])
            found = True
    if found == True:
        json2 = {
            "username": username,
            "email": email,
            "emailverified": emailverified,
            "discordid": discordid,
            "customerid": customerid,
            "avatarlink": avatarlink
        }
        return(json2)
    else:
        return("403")
@app.route('/assets/<path:path>', methods=['GET'])
def sendasset(path):
    return send_from_directory('assets', path)































@app.route('/testlogin', methods=['POST', 'GET'])
def testlogin():
    if request.method == 'GET':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        errorid = checkbanned(ip)
        if errorid != False:
            return render_template("banned.html", bannedip = ip, errorid = errorid)
        else:
            accesslog(ip)
            return render_template("login.html", ip = ip)
@app.route('/testblacklist', methods=['GET'])
def testblacklist():
    ip = request.args.get('ip')
    reason = request.args.get('reason')
    auth = request.args.get('auth')
    if auth == "REDACTED":
        if ip == None or reason == None:
            return "Missing Arguments"
        else:
            sqlcommandList.append("INSERT INTO authbannedips (ip, reason) VALUES ('" + ip + "', '" + reason + "')")
            bannediplist.append({'ip': ip, 'reason': reason})
            print("Blacklisted IP: " + ip + " Reason: " + reason)
            return "Success"
@app.route('/onduty', methods=['POST', 'GET'])
def onduty():
    if request.method == 'POST':
        total = ""
        ondutydata = str(request.data).lstrip("b'").rstrip("'")
        ondutyjson = json.loads(ondutydata)
        dutytime = str(round(time.time()))
        postal = str((ondutyjson['postal']))
        playername = (ondutyjson['name'])
        communityid = (ondutyjson['community'])
        coordy = str((ondutyjson['coordy']))
        coordx = str((ondutyjson['coordx']))
        playerSpeed = str((ondutyjson['speed']))
        playerLooking = str((ondutyjson['looking']))
        lights = str((ondutyjson['lights']))
        inveh = str((ondutyjson['inveh']))
        if len(unitlist) == 0:
            unitlist.append({"communityid": communityid, "name": playername, "postal": postal, "coordy": coordy, "coordx": coordx, "dutytime": dutytime, "speed": playerSpeed, "looking": playerLooking, "lights": lights, "inveh": inveh})
        global inlist
        inlist = False
        for i in unitlist:
            if i['name'] == playername:
                inlist = True
                total = i
            if int(dutytime) - int(i['dutytime']) > 10:
                unitlist.remove(i)
        if inlist == False:
            unitlist.append({"communityid": communityid, "name": playername, "postal": postal, "coordy": coordy, "coordx": coordx, "dutytime": dutytime, "speed": playerSpeed, "looking": playerLooking, "lights": lights, "inveh": inveh})
        else:
            unitlist.remove(total)
            unitlist.append({"communityid": communityid, "name": playername, "postal": postal, "coordy": coordy, "coordx": coordx, "dutytime": dutytime, "speed": playerSpeed, "looking": playerLooking, "lights": lights, "inveh": inveh})
        return("200")
    if request.method == 'GET':
        communityid = str(request.args.get('community'))
        returnunitlist = []
        for i in unitlist:
            if i['communityid'] == communityid:
                if i not in returnunitlist:
                    returnunitlist.append({"community": communityid, "playername": i['name'], "postal": i['postal'], "coordy": i['coordy'], "coordx": i['coordx'], "speed": i['speed'], "looking": i['looking'], "lights": i['lights'], "inveh": i['inveh']})       
        returnunitlistjson = json.loads(json.dumps(returnunitlist))
        return jsonify(returnunitlistjson)
global calllist
global callid
calllist = []
callid = 0
@app.route('/cad911', methods=['POST', 'GET'])
def cad911():
    curtime = str(round(time.time()))
    if request.method == 'POST':
        global callid
        cad911data = str(request.data).lstrip("b'").rstrip("'")
        cad911json = json.loads(cad911data)
        comkey911 = (cad911json['community'])
        playername911 = (cad911json['name'])
        postal911 = (cad911json['postal'])
        content911 = (cad911json['content'])
        content911 = content911.strip("'")
        content911 = content911.strip('"')
        calltime = str(round(time.time()))
        for i in cadCommunitiesList:
            if i['comkey'] == comkey911:
                i['911num'] = str(int(i['911num']) + 1)
                callid = i['911num']
        print(callid)
        sqlcommandList.append("UPDATE cadCommunities SET 911num = '" + str(callid) + "' WHERE comkey = '" + str(comkey911) + "'")
        calllist.append({"community": comkey911, "name": playername911, "postal": postal911, "content": content911, "calltime": calltime, "callid": callid})
        print(calllist)
        return("200")
    if request.method == 'GET':
        comkey911 = request.args.get('community')
        returncalllist = []
        for i in calllist:
            if int(curtime) - int(i['calltime']) > 1200:
                calllist.remove(i)
            else:
                if i['community'] == comkey911:
                    if i not in returncalllist:
                        returncalllist.append({"comkey": comkey911, "callername": i['name'], "location": i['postal'], "description": i['content'], "calltime": i['calltime'], "callid": i['callid']})
        returncalllistjson = json.loads(json.dumps(returncalllist))
        return jsonify(returncalllistjson)
@app.route('/cadLogin', methods=['GET'])
def cadLogin():
    found = False
    username = request.args.get('user')
    password = request.args.get('pass')
    global cadUsersList
    for i in cadUsersList:
        if i['username'] == username:
            if i['password'] == password:
                token = (i['token'])
                found = True
    if found == True:
        return(token)
    else:
        return("403")
@app.route('/cadUserInfo', methods=['GET'])
def cadUserInfo():
    found = False
    token = request.args.get('usertoken')
    global cadUsersList
    for i in cadUsersList:
        if i['token'] == token:
            communities = (str(i['communities']).replace("'", '"'))
            loginusername = (i['username'])
            found = True
    if found == True:
        json2 = {
            "loginusername": loginusername,
            "communities": communities
        }
        return(json2)
    else:
        return("403")
@app.route('/cadCommunityInfo', methods=['GET'])
def cadCommunityInfo():
    found = False
    getinfoname = request.args.get('id')
    global cadCommunitiesList
    for i in cadCommunitiesList:
        if i['comkey'] == getinfoname:
            commname = (i['commname'])
            comkey = (i['comkey'])
            owner = (i['owner'])
            num911 = (i['911num'])
            imageurl = (i['imageurl'])
            found = True
    if found == True:
        json2 = {
            "commname": commname,
            "comkey": comkey,
            "owner": owner,
            "911num": num911,
            "imageurl": imageurl
        }
        return(json2)
    else:
        return("404")
@app.route('/cadUserUpdateCommunities', methods=['POST'])
def cadUserUpdateCommunities():
    found = False
    data = str(request.data).lstrip("b'").rstrip("'")
    datajson = json.loads(data)
    token = str((datajson['usertoken']))
    communities = str((datajson['communities']))
    global cadUsersList
    for i in cadUsersList:
        if i['token'] == token:
            total = i
            cadUsersList.remove(total)
            cadUsersList.append({"username": total['username'], "password": total['password'], "token": total['token'], "communities": communities})
            sqlcommandList.append('UPDATE cadUsers SET communities = "' + communities + '" WHERE usertoken = "' + token + '"')
            sql.commit()
            found = True
    if found == True:
        return("200")
    else:
        return("403")
@app.route('/cadRegister', methods=['GET'])
def cadRegister():
    regusername = request.args.get('user')
    regpassword = request.args.get('pass')
    for i in cadUsersList:
        if i['username'] == regusername:
            return("403")
        else:
            found = False
    if found == False:
        token1 = str(uuid.uuid4())
        token2 = str(uuid.uuid4())
        token3 = str(uuid.uuid4())
        token = (token1 + token2 + token3)
        cadUsersList.append({"username": regusername, "password": regpassword, "token": token, "communities": ""})
        sqlcommandList.append("INSERT IGNORE INTO cadUsers(username, password, usertoken) VALUES ('" + regusername + "', '" + regpassword + "', '" + token + "')")
        return(token)
@app.route('/cadcivrecords', methods=['GET', 'POST'])
def cadcivrecords():
    if request.method == "POST":
        request5data = str(request.data).lstrip("b'").rstrip("'")
        request5djson = json.loads(request5data)
        firstname = str(request5djson['firstname']).lower()
        lastname = str(request5djson['lastname']).lower()
        social = str(request5djson['social'])
        communityid = str(request5djson['community'])
        recdate = str(request5djson['date'])
        type = str(request5djson['type'])
        details = str(request5djson['details'])
        recid = str(request5djson['id'])
        author = str(request5djson['author'])
        cadCivRecordsList.append({"firstname": firstname, "lastname": lastname, "social": social, "communityid": communityid, "recdate": recdate, "type": type, "details": details, "recid": recid, "author": author})
        sqlcommandList.append("INSERT IGNORE INTO cadCivRecords(firstname, lastname, social, communityid, recdate, type, details, recid, author) VALUES ('" + firstname + "', '" + lastname + "', '" + social + "', '" + communityid + "', '" + recdate + "', '" + type + "', '" + details + "', '" + recid + "', '" + author + "')")
        if type == "Arrest":
            sqlcommandList.append("Delete FROM cadCivRecords WHERE social = '" + social + "' AND communityid = '" + communityid + "' AND type = 'Warrant'")
            sqlcommandList.append("UPDATE cadCivilians SET warrant = 'falsee' WHERE social = '" + social + "'")
            for i in cadCiviliansList:
                if i['social'] == social:
                    firstname = str(i['firstname'])
                    lastname = str(i['lastname'])
                    dob = str(i['dob'])
                    social = str(i['social'])
                    gender = str(i['gender'])
                    race = str(i['race'])
                    haircolor = str(i['haircolor'])
                    build = str(i['build'])
                    height = str(i['height'])
                    communityid = str(i['communityid'])
                    phone = str(i['phone'])
                    occupation = str(i['occupation'])
                    address = str(i['address'])
                    owner = str(i['owner'])
                    warrant = "false"
                    cadCiviliansList.remove(i)
                    cadCiviliansList.append({"firstname": firstname, "lastname": lastname, "dob": dob, "social": social, "gender": gender, "race": race, "haircolor": haircolor, "build": build, "height": height, "communityid": communityid, "phone": phone, "owner": owner, "warrant": warrant, "occupation": occupation, "address": address})                                 
            for i in cadCivRecordsList:
                if i['social'] == social:
                    if i['type'] == "Warrant":
                        cadCivRecordsList.remove(i)
        if type == "Warrant":
            sqlcommandList.append("UPDATE cadCivilians SET warrant = 'true' WHERE social = '" + social + "'")

            for i in cadCiviliansList:
                if i['social'] == social:
                    firstname = str(i['firstname'])
                    lastname = str(i['lastname'])
                    dob = str(i['dob'])
                    social = str(i['social'])
                    gender = str(i['gender'])
                    race = str(i['race'])
                    haircolor = str(i['haircolor'])
                    build = str(i['build'])
                    height = str(i['height'])
                    communityid = str(i['communityid'])
                    phone = str(i['phone'])
                    occupation = str(i['occupation'])
                    address = str(i['address'])
                    owner = str(i['owner'])
                    warrant = "true"
                    cadCiviliansList.remove(i)
                    cadCiviliansList.append({"firstname": firstname, "lastname": lastname, "dob": dob, "social": social, "gender": gender, "race": race, "haircolor": haircolor, "build": build, "height": height, "communityid": communityid, "phone": phone, "owner": owner, "warrant": warrant, "occupation": occupation, "address": address})                                 
        sql.commit()
        return("200")
    if request.method == "GET":
        reclist = []
        social1 = str(request.args.get('social')).lower()
        communityid1 = str(request.args.get('communityid'))
        for i in cadCivRecordsList:
            if i['communityid'] == communityid1:
                if i['social'] == social1:
                    json2 = {
                        "firstname": i['firstname'],
                        "lastname": i['lastname'],
                        "social": i['social'],
                        "recdate": i['recdate'],
                        "type": i['type'],
                        "details": i['details'],
                        "author": i['author'],
                    }
                    reclist.append(json2)
        return jsonify(reclist)
@app.route('/cadciv', methods=['POST', 'GET'])
def cadnewciv():
    if request.method == 'POST':
        found = False
        request4data = str(request.data).lstrip("b'").rstrip("'")
        request4djson = json.loads(request4data)
        newfirstn = str(request4djson['civfname']).lower()
        newlastn = str(request4djson['civlname']).lower()
        newdob = str(request4djson['civdob'])
        newgen = str(request4djson['civgender'])
        newrace = str(request4djson['civrace'])
        newhairc = str(request4djson['civhaircolor'])
        newbuild = str(request4djson['civbuild'])
        newheight = str(request4djson['civheight'])
        newphone = str(request4djson['civphone'])
        newcivownerid = str(request4djson['usertoken'])
        newcivaddress = str(request4djson['civaddress'])
        newcivoccupation = str(request4djson['civoccupation'])
        warrant = "false"
        newcivsocial = (str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + "-" + str(random.randint(0, 9)) + str(random.randint(0, 9)) + "-" + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)))
        communityid = str(request4djson['communityid'])
        for i in cadCiviliansList:
            if i['communityid'] == communityid:
                if i['social'] == newcivsocial:
                    found = True
        if found == False:
            cadCiviliansList.append({"firstname": newfirstn, "lastname": newlastn, "dob": newdob, "social": newcivsocial, "gender": newgen, "race": newrace, "haircolor": newhairc, "build": newbuild, "height": newheight, "communityid": communityid, "phone": newphone, "owner": newcivownerid, "warrant": warrant, "occupation": newcivoccupation, "address": newcivaddress})                                 
            sqlcommandList.append("INSERT IGNORE INTO cadCivilians(firstname, lastname, dateofbirth, gender, race, haircolor, build, height, phone, owner, social, communityid, warrant, address, occupation) VALUES ('" + newfirstn + "', '" + newlastn + "', '" + newdob + "', '" + newgen + "', '" + newrace + "', '" + newhairc + "', '" + newbuild + "', '" + newheight + "', '" + newphone + "', '" + newcivownerid + "', '" + newcivsocial + "', '" + communityid + "', '" + warrant + "', '" + newcivaddress + "', '" + newcivoccupation + "')")
            return('200')
        else:
            return('400')
    if request.method == 'GET':
        civlist = []
        firstname1 = str(request.args.get('firstname')).lower()
        lastname1 = str(request.args.get('lastname')).lower()
        communityid1 = str(request.args.get('communityid'))
        for i in cadCiviliansList:
            if communityid1 == i['communityid']:
                if firstname1 == i['firstname']:
                    if lastname1 == i['lastname']:
                        civlist.append(i)
                        print(i['social'])
        return jsonify(civlist)
@app.route('/cadcivself', methods=['POST', 'GET'])
def cadcivself():
    if request.method == 'GET':
        civlist2 = []
        curtoken = str(request.args.get('token'))
        communityid2 = str(request.args.get('communityid'))
        for i in cadCiviliansList:
            if i['communityid'] == communityid2:
                if i['owner'] == curtoken:
                    civlist2.append(i)
        return jsonify(civlist2)
@app.route('/cadcivedit', methods=['POST', 'GET'])
def cadcivedit():
    if request.method == 'GET':
        curtoken = str(request.args.get('token'))
        communityid3 = str(request.args.get('communityid'))
        social3 = str(request.args.get('social'))
        for i in cadCiviliansList:
            if i['communityid'] == communityid3:
                if i['social'] == social3:
                    if i['owner'] == curtoken:
                        return jsonify(i)
    if request.method == 'POST':
        warrant = "false"
        request4data = str(request.data).lstrip("b'").rstrip("'")
        request4djson = json.loads(request4data)
        newfirstn = str(request4djson['civfname']).lower()
        newlastn = str(request4djson['civlname']).lower()
        newdob = str(request4djson['civdob'])
        newgen = str(request4djson['civgender'])
        newrace = str(request4djson['civrace'])
        newhairc = str(request4djson['civhaircolor'])
        newbuild = str(request4djson['civbuild'])
        newheight = str(request4djson['civheight'])
        newphone = str(request4djson['civphone'])
        newaddress = str(request4djson['civaddress'])
        newoccupation = str(request4djson['civoccupation'])
        newcivownerid = str(request4djson['usertoken'])
        newcivsocial = str(request4djson['civsocial'])
        communityid = str(request4djson['communityid'])
        for i in cadCiviliansList:
            if i['communityid'] == communityid:
                if i['social'] == newcivsocial:
                    if i['warrant'] == "true":
                        warrant = "true"
                    cadCiviliansList.remove(i)
        sqlcommandList.append("UPDATE cadCivilians set firstname = '" + newfirstn + "', lastname = '" + newlastn + "', dateofbirth = '" + newdob + "', social = '" + newcivsocial + "', gender = '" + newgen + "', race = '" + newrace + "', haircolor = '" + newhairc + "', build = '" + newbuild + "', height = '" + newheight + "', communityid = '" + communityid + "', phone = '" + newphone + "', owner = '" + newcivownerid + "', warrant = '" + warrant + "', occupation = '" + newoccupation + "', address = '" + newaddress + "' WHERE communityid = '" + communityid + "' AND social = '" + newcivsocial + "' AND owner = '" + newcivownerid + "'")
        cadCiviliansList.append({"firstname": newfirstn, "lastname": newlastn, "dob": newdob, "social": newcivsocial, "gender": newgen, "race": newrace, "haircolor": newhairc, "build": newbuild, "height": newheight, "communityid": communityid, "phone": newphone, "owner": newcivownerid, "warrant": warrant, "occupation": newoccupation, "address": newaddress})                                 
        return('200')
@app.route('/cadalpr', methods=['GET'])
def cadalpr():
    found = "false"
    lplate = str(request.args.get('lplate')).lower().lstrip("_").rstrip("_")
    communityid = str(request.args.get('communityid'))
    firstname3 = "unknown"
    lastname3 = "unknown"
    warrant3 = "false"
    stolen = "false"
    for i in cadCarsList:
        if i['communityid'] == communityid:
            if i['lplate'] == lplate:
                social = i['social']
                stolen = i['stolen']
                found = "true"
                for i in cadCiviliansList:
                    if i['communityid'] == communityid:
                        if i['social'] == social:
                            firstname3 = i['firstname']
                            lastname3 = i['lastname']
                            warrant3 = i['warrant']
    if found == "false":
        return("404")

    alprjson = {
            "firstname": firstname3,
            "lastname": lastname3,
            "plate": lplate,
            "warrant": warrant3,
            "stolen": stolen,
            }
    return jsonify(alprjson)
@app.route('/cadcars', methods=['POST', 'GET'])
def cadcars():
    if request.method == "GET":
        carslist = []
        social1 = str(request.args.get('social')).lower()
        communityid1 = str(request.args.get('communityid'))
        for i in cadCarsList:
            if i['communityid'] == communityid1:
                if i['social'] == social1:
                    make = i['make']
                    model = i['model']
                    color = i['color']
                    lplate = i['lplate']
                    social = i['social']
                    stolen = i['stolen']
                    if stolen is None:
                        stolen = "No"
                    if stolen == "false":
                        stolen = "No"
                    if stolen == "true":
                        stolen = "Yes"
                    carslist.append({"make": make, "model": model, "color": color, "lplate": lplate, "social": social, "stolen": stolen})
        return jsonify(carslist)
    if request.method == "POST":
        found = "false"
        newcardata = str(request.data).lstrip("b'").rstrip("'")
        newcardatajson = json.loads(newcardata)
        newcarsocial = (newcardatajson['social'])
        newcarmake = (newcardatajson['make'])
        newcarmodel = (newcardatajson['model'])
        newcarcolor = (newcardatajson['color'])
        newcarlplate = (newcardatajson['lplate']).lower()
        newcarreqtype = (newcardatajson['reqtype'])
        newcarcommunity = (newcardatajson['communityid'])
        if newcarreqtype == "new":
            for i in cadCarsList:
                if i['communityid'] == newcarcommunity:
                    if i['lplate'] == newcarlplate:
                        found = "true"
            if found == "false":
                sqlcommandList.append("INSERT IGNORE INTO cadCars(make, model, color, lplate, social, communityid) VALUES ('" + newcarmake + "', '" + newcarmodel + "', '" + newcarcolor + "', '" + newcarlplate + "', '" + newcarsocial + "', '" + newcarcommunity + "')")
                cadCarsList.append({"make": newcarmake, "model": newcarmodel, "color": newcarcolor, "lplate": newcarlplate, "social": newcarsocial, "communityid": newcarcommunity, "stolen": "false"})
                return('200')
            if found == "true":
                return('400')
@app.route('/shotspotter', methods=['POST', 'GET'])
def shotspotter():
    if request.method == "POST":
        newshotspotter = str(request.data).lstrip("b'").rstrip("'")
        newshotspotterjson = json.loads(newshotspotter)
        community = str(newshotspotterjson['community'])
        postal = str(newshotspotterjson['postal'])
        coordx = str(newshotspotterjson['coordx'])
        coordy = str(newshotspotterjson['coordy'])
        receivedtime = (round(time.time()))
        
