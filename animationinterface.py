#TODO: TO BE REMOVED
from pymongo import MongoClient
client= MongoClient("mongodb+srv://admin:admin123@tmsbackendcluster-o35c6.gcp.mongodb.net/test?retryWrites=true&w=majority")
from bson.objectid import ObjectId
db=client.get_database('tms_db')
##############
def getAction(db, animcharData):
    records = db.action_collection
    records_anim = db.animation_collection
    animations = animcharData["animations"]
    characters = animcharData["characters"]
    for anim in animations:
        action_records = list(records.find({"name": anim["name"]}))
        if "action_id" in anim:
            action_record = records.find_one({"_id": ObjectId(anim["action_id"])})

        else:
            max = -1
            best_index = -1
            for roles_index in range(len(action_records)):
                count = 0
                for role in anim["roles"]:
                    if role in action_records[roles_index]:
                        count += 1

                if count > max:
                    best_index = roles_index

            action_record = action_records[best_index]

        if action_record:
            rolesdict = anim["roles"]

            for role in rolesdict:
                for character in rolesdict[role]:
                    print(character)
                    bio = characters[character]["bio"]
                    if role in action_record and bio in action_record[role] and action_record[role][bio]:
                        anim["anim_" + character] = records_anim.find_one({"_id": ObjectId(action_record[role][bio])})
        else:
            if "action_id" in anim:
                del anim["action_id"]
    return animcharData


def createOrUpdateAction(db, animCharData):
    records = db.action_collection
    records_anim = db.animation_collection
    animations = animCharData["animations"]
    characters = animCharData["characters"]
    for anim in animations:
        action_dict = {"name": anim["name"]}
        for role in anim["roles"]:
            action_dict[role] = {"Person": None, "Organism": None, "PhysicalObject": None}
            for character in anim["roles"][role]:
                if "anim_"+character not in anim:
                    temp=None
                else:
                    temp=anim["anim_" + character]
                if temp:
                    id = records_anim.insert_one(temp).inserted_id

                else:
                    id=None
                action_dict[role][characters[character]["bio"]] = id
        if "action_id" in anim and anim["action_id"]:
            action_id=anim["action_id"]
            records.update({"_id":ObjectId(action_id)},action_dict)
        else:
            print(action_dict)
            action_id = records.insert_one(action_dict).inserted_id
        anim["action_id"] = action_id
    return animCharData


def getAnimations(db, bio):
    records_anim = db.animation_collection
    return list(records_anim.find({"bio": bio}))

#
# animchardata = {
#     "animations": [
#         {   "action_id":ObjectId('5ea9285bfe758d3c5803331c'),
#             "name": "walk",
#             "prep_across": "",
#             "roles": {
#                 "Location": [
#                     "ground"
#                 ],
#                 "Theme": [
#                     "tiger"
#                 ]
#             }
#         },
#         {
#             "name": "eat",
#             "roles": {
#                 "Agent": [
#                     "tiger"
#                 ],
#                 "Patient": [
#                     "cat"
#                 ]
#             }
#         }
#     ],
#     "characters": {
#         "cat": {
#             "bio": "Organism",
#             "type": "Goat"
#         },
#         "ground": {
#             "bio": "Organism",
#             "type": "Grass"
#         },
#         "tiger": {
#             "bio": "Organism",
#             "type": "Lion"
#         }
#     }
# }
# print(getAction(db,animchardata))

