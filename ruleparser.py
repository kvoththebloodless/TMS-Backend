import utility
# TODO: Common entities to be added to the database or FRED to be used to do entity recognition
COMMON_NAMES_PERSON = ["john", "jack", "liam", "andy", "matt", "corey", "tom", "lydia", "lindsay", "stephanie", "will",
                       "annie", "gourav", "joe", "michel", "she", "he","man","woman"]
COMMON_ORGANISMS = ["rabbit", "rat", "unicorn", "monkey", "goat", "horse", "donkey", "sheep"]


def match(data, db):
    records = db.rules_collection
    animationlist = []
    charDictList = {}
    for element in data["pos_line"]["v"]:
        verb = element[0:len(element) - 2]

        posline = data["pos_line"]["line"]
        listOfrules = list(records.find({'name': verb}))

        posline = utility.formatPosline(posline, verb)

        newanimationlist, newcharDictList = utility.matchStructure(listOfrules, posline, COMMON_NAMES_PERSON,
                                                                   COMMON_ORGANISMS)

        if newanimationlist is not None and len(newanimationlist) != 0:
            animationlist.append(newanimationlist)
        if newcharDictList is not None and len(newcharDictList) != 0:
            charDictList.update(newcharDictList)

    return animationlist, charDictList


def create(animcharData, data, db):
    records = db.rules_collection
    animations = animcharData["animations"]
    for anim in range(len(animations)):
        ruledict = utility.ruleCreationLogic(animations[anim], data)
        print(ruledict)
        ruledict["action_id"]=animations[anim]["action_id"]
        id = records.insert_one(ruledict)

        animcharData["animations"][anim]["rule_id"] = id
    return animcharData
    # rule={"name":anim["name"]
    #       "roles": }


animchardata = {
    "animations": [
        {   "action_id":"123123123",
            "name": "walk",
            "prep_across": "",
            "roles": {
                "Location": [
                    "grass_1"
                ],
                "Theme": [
                    "lion_1"
                ]
            }
        },
        {   "action_id":"123123123",
            "name": "eat",
            "roles": {
                "Agent": [
                    "lion_1"
                ],
                "Patient": [
                    "goat_1"
                ]
            }
        }
    ],
    "characters": {
        "goat_1": {
            "bio": "Organism",
            "type": "Goat"
        },
        "grass_1": {
            "bio": "Organism",
            "type": "Grass"
        },
        "lion_1": {
            "bio": "Organism",
            "type": "Lion"
        }
    }
}

print(match( {"pos_line": {
    "line": [('The', 'DET'), ('lion', 'NN'), ('walked', 'VBD'), ('across','IN'),('The', 'DT'), ('grass', 'NN'),
             ('to', 'IN'), ('eat', 'VBN'),('the','DET'),('goat','NN')],
    "v": ["walk_1", "eat_1"]}}, db))
#
# def addRule(data,animationDict)
