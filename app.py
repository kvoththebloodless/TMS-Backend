import os
from flask import Flask, redirect, url_for, request, jsonify
from pymongo import MongoClient
import utility as utility
import TMSParser as par
import json
import animationinterface
import ruleparser
app = Flask("TMSBackend")
app.debug = True
client= MongoClient("MONGO_ATLAS_URL")
db=client.get_database('tms_db')

# To change accordingly 
# print(os.environ)
# client = MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
# db = client.appdb

#List of calls:-
#storyline
#characteredit
#animation edit
#animation file edit
#animfile
#autocompletenoun - now to be taken care of at the frontend

@app.route("/storyline",methods=["POST","GET"])
def storyline():
    # _items = db.appdb.find()
    # items = [items for items in _items]

    #processing text to return data :{line: text, pos_line:{n:[],v:[],adj:[{n:JJ},{n:JJ}],cd:[{n:CD}],pronoun_line:text}
    #preprocess also makes sure that verbs are written with _number in the increasing order in which they appear
    if request.method == 'POST':
        data,charDictList=utility.preprocess(request.json)

    else:
        line={"data":{"line":request.args.get("line")},"animCharDict":{}}
        linejson=jsonify(line)

        data, charDictList=utility.preprocess(linejson.json)
    if data == None:
        return jsonify({"error": "Text is empty, I wanna hear your story!"})
    result = par.parse(data, charDictList,db)
    return json.dumps(result,default=str)

@app.route("/",methods=["GET"])
def index():
    return jsonify({"Welcome": "Just add your text in the URL like so : '/storyline?line=<Your text>' "})

@app.route("/sampleanim", methods=["GET"])
def getSampleAnim():
    bio=request.args.get("bio")

    result_animDict=animationinterface.getAnimations(db,bio)
    return json.dumps(result_animDict,default=str)

@app.route("/action", methods=["POST"])
def fetchAction():
    animCharDict=request.json
    result_anim=animationinterface.getAction(db,animCharDict)

    return json.dumps(result_anim,default=str)

@app.route("/edit", methods=["POST"])
def animAndRuleEdit():
    animCharDictData=request.json
    animCharDict=animCharDictData["animCharDict"]
    data=animCharDictData["data"]
    animCharDict=animationinterface.createOrUpdateAction(db,animCharDict)
    animCharDict=ruleparser.create(animCharDict,data,db)

    return json.dumps(animCharDict,default=str)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)


