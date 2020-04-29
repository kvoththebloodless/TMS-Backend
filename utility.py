import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
Nouns = ["NN", "NNS", "NNP", "NNPS", "PRP"]
Adjectives = ["JJ", "JJR", "JJS"]
prepositions = ['about',
                'above',
                'according to',
                'across',
                'after',
                'against',
                'ago',
                'ahead of',
                'along',
                'amidst',
                'among',
                'amongst',
                'apart',
                'around',
                'as',
                'as far as',
                'as well as',
                'aside',
                'at',
                'away',
                'because of',
                'before',
                'behind',
                'below',
                'beneath',
                'beside',
                'besides',
                'between',
                'beyond',
                'by',
                'by means of',
                'by way of',
                'close to',
                'despite',
                'down',
                'due to',
                'during',
                'except',
                'for',
                'from',
                'hence',
                'in',
                'in accordance with',
                'in addition to',
                'in case of',
                'in front of',
                'in lieu of',
                'in place of',
                'in regard to',
                'in spite of',
                'in to',
                'inside',
                'instead of',
                'into',
                'like',
                'near',
                'next',
                'next to',
                'notwithstanding',
                'of',
                'off',
                'on',
                'on account of',
                'on behalf of',
                'on to',
                'on top of',
                'onto',
                'opposite',
                'out',
                'out from',
                'out of',
                'outside',
                'over',
                'owing to',
                'past',
                'per',
                'prior to',
                'round',
                'since',
                'than',
                'through',
                'throughout',
                'till',
                'to',
                'toward',
                'towards',
                'under',
                'underneath',
                'unlike',
                'until',
                'unto',
                'up',
                'upon',
                'via',
                'with',
                'with a view to',
                'within',
                'without',
                'worth']
Verbs = ["VB",
         "VBD",
         "VBG",
         "VBN",
         "VBP",
         "VBZ"]

roles = ["Actor", "Patient", "Agent", "Instrument", "Location", "Cause", "Actor1", "Actor2"
    , "Asset", "Beneficiary", "Destination", "Oblique", "Material", "Patient1", "Patient2"
    , "Predicate", "Product", "Recipient", "Source", "Theme", "Theme1",
         "Theme2", "Time", "Topic", "Value"]


def formatFredResponse(response, newdict={}):
    for key in response:
        newkey = dTH(key)
        if type(response[key]) is list and type(response[key][0]) is dict:
            newdict[newkey] = []
            for item in response[key]:
                newdict[newkey].append(formatFredResponse(item, {}))
        elif type(response[key]) is dict:
            newdict[newkey] = formatFredResponse(response[key], {})
        else:
            newdict[newkey] = dTH(response[key])

    return newdict
def remove_(word):
    return(word.split("_")[0])


def ruleCreationLogic(anim,data):

     posline=data["pos_line"]["line"][0:]

     animroles=anim["roles"]
     newposline=posline[0:]
     for element in range(len(posline)):
        if posline[element][1] in Verbs:
            newposline[element] = (returnLemmatized(posline[element][0],"v"),posline[element][1])
        else:
         newposline[element] = ("", posline[element][1])
        for role in animroles:

            if posline[element][0] in list(map(remove_,animroles[role])):
                newposline[element]=(role,posline[element][1])
                break


     rolesass = sendCleanedUpTagsNounAndVerb(anim["name"], newposline)
     rule={"name":anim["name"], "roles":rolesass}
     return rule

def sendCleanedUpTagsNounAndVerb(verb,line):

    rule=[]
    for element in line:
        dict={}
        if element[1] in Nouns:
            dict["NN"]=element[0]
        elif element[1] in Verbs:

            if element[0] !=verb:
                if element[0] in ["was", "is", "were", "be"]:
                    dict["BE"]=""
                else:
                    dict["NEGV"]=""
            else:
                dict["v"]="name"
        else:
            dict[element[1]]=element[0]
        rule.append(dict)
    return rule
def findTagForWordFromPosLine(word,line):
    for element in line:
        if element[0]==word:
            return element[1]
    return -1
def dTH(key):
    if "#" in key:
        return key.split("#")[1]
    if "/" in key and "w3" not in key:
        temp = key.split("/")
        return temp[len(temp) - 1]
    else:
        return key


def extractAndAddHiddenVerbs(data, response):
    for key in response:
        type = findTypeOfWord(key[0:len(key) - 2])
        verb = lemmatizer.lemmatize(key[0:len(key) - 2], "v") + (key[len(key) - 2:])

        if "VB" in type and verb not in data["pos_line"]["v"]:
            data["pos_line"]["v"].append(key)

    return data


def preprocess(response):
    data = response["data"]
    characterDictList = response["characterDictList"]
    temp = str(data["line"]).split(" ")
    tempstr = ""

    for element in temp:

        if "," in element:
            element = element.replace(",", " and ")
            element = element.strip()

        tempstr += element + " "

    tempstr = tempstr.strip()
    temp = tempstr.split(" ")
    data["line"] = tempstr

    if "pos_line" not in data:
        data["pos_line"] = {}
        tempnlp = nltk.word_tokenize(data["line"])
        tempnlp = nltk.pos_tag(tempnlp)

        tempdict = {"n": [], "v": []}

        countdict = {}

        for element in range(len(tempnlp)):

            lemmatizedVerb = lemmatizer.lemmatize(temp[element], "v")
            if lemmatizedVerb in ["was", "is", "were", "be"]:
                tempnlp[element] = (tempnlp[element][0], "BE")
                continue
            if tempnlp[element][1] in Nouns:
                tempdict["n"].append(temp[element])

            if tempnlp[element][1] in Verbs:
                if lemmatizedVerb in countdict:
                    countdict[lemmatizedVerb] = countdict[lemmatizedVerb] + 1
                else:
                    countdict[lemmatizedVerb] = 1

                tempdict["v"].append(lemmatizedVerb + "_" + str(countdict[lemmatizedVerb]))

        data["pos_line"]["line"] = tempnlp
        data["pos_line"].update(tempdict)
    return data, characterDictList


def checkForPrepositionAfterVerb(data, key, verbresponse):
    for tag in verbresponse:
        if tag in prepositions:
            return tag
    pos_tags = data["pos_line"]["line"]
    count = 0

    index = int(key[len(key) - 1:])

    verb = key[0:len(key) - 2]

    for i in range(len(pos_tags)):

        if verb in lemmatizer.lemmatize(pos_tags[i][0], "v"):

            count += 1

            if count == index and i + 1 < len(pos_tags) and (
                    pos_tags[i + 1] == "IN" or pos_tags[i + 1][0] in prepositions):
                return pos_tags[i + 1][0]
    return None


def orderResponseByinstance(sitResp):
    orderedlist = []
    for tag in sitResp:
        if "_" in tag["value"]:
            orderedlist.insert(0, tag)
        else:
            orderedlist.append(tag)
    return orderedlist


def checkForPrepositionInKeyNonv(response, tag):
    for key in response:

        if key in prepositions or tag in key and key.replace("tag", ""):
            return key
    return None


def findTypeOfWord(word):
    text = nltk.word_tokenize(word)

    type = nltk.pos_tag(text)[0][1]
    return type


def returnLemmatized(word, type):
    return lemmatizer.lemmatize(word, type)


def matchStructure(rules, posline, COMMON_PERSON_NAME, COMMON_ANIMAL):
    # Direct matching
    animlist, chardictlist = matchStructureSubfunc(rules, posline, COMMON_PERSON_NAME, COMMON_ANIMAL, False)
    # Try again with determiners, prepositions and everything except nouns and verbs stripped away
    if animlist == None or len(animlist) == 0:
        posline = stripPosToBareMinInLine(posline)
        animlist, chardictlist = matchStructureSubfunc(rules, posline, COMMON_PERSON_NAME, COMMON_ANIMAL, True)
    return animlist, chardictlist


def stripPosToBareMinInLine(posline):
    newposline = []
    for element in posline:
        if element[1] == "NN" or element[1] == "v":
            newposline.append(element)
    return newposline


def stripPosToBareMinInResponse(roles):
    newroles = []
    for element in roles:
        if "NN" in element or "v" in element:
            newroles.append(element)
    return newroles


def matchStructureSubfunc(rules, posline, COMMON_PERSON_NAME, COMMON_ANIMAL, strip):
    anim = {}
    charlist = {}
    finalrule=None
    for rule in rules :
        if finalrule:
            break
        ruledata = rule["roles"]

        if strip:
            ruledata = stripPosToBareMinInResponse(ruledata)

        if len(ruledata) == len(posline):
            for i in range(len(posline)):

                if posline[i][1] in ruledata[i]:
                    if ruledata[i][posline[i][1]]:
                        if ruledata[i][posline[i][1]] not in anim:
                            anim[ruledata[i][posline[i][1]]] = posline[i][0]

                        else:
                            anim[ruledata[i][posline[i][1]]].append(posline[i][0])

                        if posline[i][1] in Nouns:
                            if posline[i][0].lower() in COMMON_PERSON_NAME:
                                charlist[posline[i][0]] = {"bio": "Person"}
                            elif posline[i][0].lower() in COMMON_ANIMAL:
                                charlist[posline[i][0]] = {"bio": "Organism"}
                            else:
                                charlist[posline[i][0]] = {"bio": "PhysicalObject"}
                    if i == len(posline)-1:
                        finalrule=rule


                else:
                    anim = {}
                    charlist = {}
    anim["action_id"]=finalrule["action_id"]
    anim["rule_id"]=finalrule["_id"]
    return anim, charlist


def formatPosline(posline, verb):
    posline = posline[0:]
    for element in range(len(posline)):

        if posline[element][1] in Nouns:

            posline[element] = (posline[element][0], "NN")
        elif posline[element][1] in Verbs:
            lemmetized = returnLemmatized(posline[element][0], "v")
            if lemmetized != verb:
                if posline[element][0] in ["was", "is", "were", "be"]:
                    posline[element] = (lemmetized, "BE")
                else:
                    posline[element] = (lemmetized, "NEGV")
            else:

                posline[element] = (lemmetized, "v")


    return posline
# print(orderResponseByinstance([
#     {
#         "value": "Day",
#         "type": "uri"
#     },
#     {
#         "value": "sunny_2",
#         "type": "uri"
#     },
#     {
#         "value": "#SunnyDay",
#         "type": "uri"
#     },
#
#     {
#         "value": "there_1",
#         "type": "uri"
#     }
# ]))

# print(checkForPrepositionAfterVerb({'line': 'once upon a time i kicked a guy and he kicked over me',
#                                     'pos_line': {'line': 'RB IN DT NN NN VBD DT NN CC PRP VBD IN PRP',
#                                                  'n': ['time', 'i', 'guy'], 'v': ['kick_1', 'kick_2']}}, "kick_2"))
