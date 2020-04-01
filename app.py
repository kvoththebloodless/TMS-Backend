import os
from flask import Flask, redirect, url_for, request, jsonify
from pymongo import MongoClient
import utility as utility
import TMSParser as par

app = Flask("TMSBackend")
app.debug = True
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
        line={"data":{"line":request.args.get("line")},"characterDictList":{}}
        linejson=jsonify(line)

        data, charDictList=utility.preprocess(linejson.json)
    if data == None:
        return jsonify({"error": "Text is empty, I wanna hear your story!"})
    result = par.parse(data, charDictList)
    return jsonify(result)

@app.route("/",methods=["GET"])
def index():
    return jsonify({"Welcome": "Just add your text in the URL like so : '/storyline?line=<Your text>' "})
@app.route("/characteredit", methods=["POST"])
def characterEdit():
    charDict=request.json
    result_charDict=par.getCharInstance().typeLogic(charDict)

    return jsonify(result_charDict)

@app.route("/animedit", methods=["POST"])
def animEdit():
    animDict,data=utility.preprocess(request.json)
    result_animDict=par.getAnimInstance().updateRule(animDict,data)

    return jsonify(result_animDict)

@app.route("/animfiledit", methods=["POST"])
def animfiledit():
    animJson,animId,data=utility.preprocess(request.json)
    result_anim=par.getAnimInstance().editAnimation(animJson,animId,data)

    return jsonify(result_anim)

@app.route("/animfile", methods=["POST"])
def animFilEdit():
    animId,data=utility.preprocess(request.json)
    result_anims=par.getAnimInstance().getAnimations(animId,data)

    return jsonify(result_anims)      

# def storylinetemp(data):
#     data, charDictList = utility.preprocess(data)
#     if data == None:
#         return jsonify({"error": "Text is empty, I wanna hear your story!"})
#     result = par.parse(data, charDictList)
#     print(result)
#     return jsonify(result)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)


