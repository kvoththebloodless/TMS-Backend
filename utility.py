import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
Nouns = ["NN", "NNS", "NNP", "NNPS"]
Adjectives = ["JJ", "JJR", "JJS"]
prepositions=[ 'about' ,
 'above' ,
 'according to' ,
 'across' ,
 'after' ,
 'against' ,
 'ago' ,
 'ahead of' ,
 'along' ,
 'amidst' ,
 'among' ,
 'amongst' ,
 'apart' ,
 'around' ,
 'as' ,
 'as far as' ,
 'as well as' ,
 'aside' ,
 'at' ,
 'away' ,
 'because of' ,
 'before' ,
 'behind' ,
 'below' ,
 'beneath' ,
 'beside' ,
 'besides' ,
 'between' ,
 'beyond' ,
 'by' ,
 'by means of' ,
 'by way of' ,
 'close to' ,
 'despite' ,
 'down' ,
 'due to' ,
 'during' ,
 'except' ,
 'for' ,
 'from' ,
 'hence' ,
 'in' ,
 'in accordance with' ,
 'in addition to' ,
 'in case of' ,
 'in front of' ,
 'in lieu of' ,
 'in place of' ,
 'in regard to' ,
 'in spite of' ,
 'in to' ,
 'inside' ,
 'instead of' ,
 'into' ,
 'like' ,
 'near' ,
 'next' ,
 'next to' ,
 'notwithstanding' ,
 'of' ,
 'off' ,
 'on' ,
 'on account of' ,
 'on behalf of' ,
 'on to' ,
 'on top of' ,
 'onto' ,
 'opposite' ,
 'out' ,
 'out from' ,
 'out of' ,
 'outside' ,
 'over' ,
 'owing to' ,
 'past' ,
 'per' ,
 'prior to' ,
 'round' ,
 'since' ,
 'than' ,
 'through' ,
 'throughout' ,
 'till' ,
 'to' ,
 'toward' ,
 'towards' ,
 'under' ,
 'underneath' ,
 'unlike' ,
 'until' ,
 'unto' ,
 'up' ,
 'upon' ,
 'via' ,
 'with' ,
 'with a view to' ,
 'within' ,
 'without' ,
 'worth']
Verbs = ["VB",
         "VBD",
         "VBG",
         "VBN",
         "VBP",
         "VBZ"]


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


def dTH(key):
    if "#" in key:
        return key.split("#")[1]
    if "/" in key and "w3" not in key:
        temp = key.split("/")
        return temp[len(temp) - 1]
    else:
        return key


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

        print(tempnlp)
        countdict= {}
        for element in range(len(tempnlp)):


            if tempnlp[element][1] in Nouns:
                tempdict["n"].append(temp[element])

            if tempnlp[element][1] in Verbs and lemmatizer.lemmatize(temp[element], "v") not in ["was", "is", "were",
                                                                                                 "be", "want"]:
                if lemmatizer.lemmatize(temp[element], "v") in countdict:
                    countdict[lemmatizer.lemmatize(temp[element], "v")] = countdict[lemmatizer.lemmatize(temp[element],
                                                                                                         "v")] + 1
                else:
                    countdict[lemmatizer.lemmatize(temp[element], "v")]=1
                tempdict["v"].append(lemmatizer.lemmatize(temp[element], "v") + "_" + str(countdict[lemmatizer.lemmatize(temp[element], "v")]))


        data["pos_line"]["line"] = tempnlp
        data["pos_line"].update(tempdict)
    return data, characterDictList


def checkForPrepositionAfterVerb(data, key):

    pos_tags = data["pos_line"]["line"]
    count = 0

    index = int(key[len(key) - 1:])

    verb = key[0:len(key) - 2]

    for i in range(len(pos_tags)):


        if verb in lemmatizer.lemmatize(pos_tags[i][0],"v"):

            count += 1

            if count == index and i + 1 < len(pos_tags) and( pos_tags[i + 1] == "IN" or pos_tags[i+1][0] in prepositions):

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
def checkForPrepositionInKeyNonv(response,tag):

    for key in response:

        if key in prepositions or tag in key and key.replace("tag",""):
            return key
    return None
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
