import requests
import utility as utility
import copy

from os import environ
bearer=environ.get('FRED API TOKEN')
URL = "http://wit.istc.cnr.it/stlab-tools/fred?"
params1 = {
    "findrelations": True,
    "semantic-subgraph": True,
    'wsd': True,
    "textannotation": "earmark",
    "prefix": "fred",

}
Roles = ["Agent", "Actor", "Actor1", "Actor2", "Agent", "Beneficiary", "Experiencer", "Patient1", "Patient2",
         "Instrument", "Theme1", "Theme2", "Theme", "Location", "Attribute", "Cause", "Extent", "Stimulus", "Material",
         "Topic", "Predicate", "Value", "Patient"]


def parse(data, charDictList, charinterface):
    params1.update({"text": data["line"]})

    response = requests.get(url=URL, params=params1, headers={"Accept": "application/rdf+json",
                                                              "Authorization": bearer})
    response = response.json()

    response = utility.formatFredResponse(response)

    # First we parse the verbs
    animdictlist, charDictList = parseVerbs(data, response, charDictList)
    # Second we parse situation and event
    charDictList = parseSituations(data, response, charDictList)
    # Third we look for there clause
    charDictList = parseTheres(data, response, charDictList)
    # Finally to catch any stragglers
    # charDictList, names = parseAnys(data, response, charDictList, charinterface)

    # Todo: name tag handling
    # Todo:Make typelogic in charinterface
    # Call typeLogic in characterinterface to load the accessories based on type parameter in all chardict
    # charinterface.typeLogic(charDictList)
    return charDictList, animdictlist


def parseVerbs(data, response, charDictList):
    animDictList = []
    for verb in data["pos_line"]["v"]:

        if "visited" in response[verb] and response[verb]["visited"] == True:
            continue
        verbResponse = response[verb]
        animDict = {"name": verb[0:len(verb) - 1], "roles": {}}

        for key in verbResponse:

            # If Role
            if key in Roles:
                animDict["roles"][key] = []
                for field in verbResponse[key]:
                    print(field["value"])
                    charDictList, names = deepDive(field["value"], response, charDictList, data)
                    if names is not None and len(names) != 0:
                        animDict["roles"][key].append(names)

            # Does Animation have a quality?
            if key == "hasQuality":
                animDict["quality"] = []
                for field in verbResponse[key]:
                    animDict["quality"].append(field["value"])

            # Is Animation attached to a quantity, for now we will assume it to be the number of times
            if key == "hasDataValue":
                animDict["repeat"] = []
                for field in verbResponse[key]:
                    animDict["repeat"] = verbResponse[key]["value"]
            # is there a truth value associated with the animation
            if key == "hasTruthValue" and verbResponse[key]["value"] == False:
                animDict = None

        prep = utility.checkForPrepositionAfterVerb(data, verb)
        if prep is not None:
            animDict["preposition"]=prep
        # Mark Node as visited and add animation to list
        verbResponse["visited"] = True
        if animDict is not None:
            animDictList.append(animDict)
    return animDictList, charDictList


def deepDive(key, response, charDictList, data):
    if "there" in key and "visited" not in response[key]:
        charDictList, names = parseThere(key, data, response, charDictList)
    elif "situation" in key and "visited" not in response[key]:
        charDictList, names = parseSituation(key, data, response, charDictList)
        # TODO: implement this method in utility
    else:
        charDictList, names = parseAny(key, data, response, charDictList)

    return charDictList, names


def parseSituation(key, data, response, charDictList):
    situationResponse = response[key]
    namelist = []
    if "visited" in situationResponse and situationResponse[
        "visited"] == True or "hasTruthValue" in situationResponse and \
            situationResponse["hasTruthValue"] == False:
        return charDictList, None

    if "involves" in situationResponse:

        # Todo: Utility function to order keys by instance tag first returns a list
        for field in utility.orderResponseByinstance(situationResponse["involves"]):
            charDictList, names = deepDive(field["value"], response, charDictList, data)
            if names is not None and len(names) != 0:
                namelist.extend(names)

    prepkey = utility.checkForPrepositionInKeyNonv(situationResponse)

    if prepkey != None:
        for field in situationResponse[prepkey]:
            charDictList, names = deepDive(field["value"], response, charDictList, data)
            if names is not None and len(names)!=0:
                namelist.extend(names)
        for name in namelist:

            charDictList[name]["prep_"+prepkey] = names

    situationResponse["visited"] = True
    return charDictList, namelist


def parseThere(key, data, response, charDictList):
    thereResponse = response[key]
    namelist = []
    if "visited" in thereResponse and thereResponse["visited"] == True or "hasTruthValue" in thereResponse and \
            thereResponse["hasTruthValue"] == False:
        return charDictList, None

    if "type" in thereResponse:
        for field in thereResponse["type"]:
            if field["value"] == "There":
                continue
            charDictList, names = deepDive(field["value"], response, charDictList, data)
            if names is not None and len(names) != 0:
                namelist.extend(names)
    if "hasQuality" in thereResponse:

        for index in range(0, len(namelist)):
            if "descriptors" not in charDictList[namelist[index]] or charDictList[namelist[index]][
                "descriptors"] is None:
                charDictList[namelist[index]]["descriptors"] = []
            for quality in thereResponse["hasQuality"]:
                charDictList[namelist[index]]["descriptors"].append(quality["value"])
    # if "hasQuantifier" in thereResponse: TODO: to be implemented for "some" or "many"

    # if "hasDataValue" in thereResponse:
    #     for name in namelist:
    #         if name not in data["pos_line"]["CD"]:
    #             continue
    #         for numOfCopies in range(int(data["pos_line"]["CD"][name])):
    #             newCopy = copy.deepcopy(charDictList[namelist[index]])
    #             charDictList[namelist[index] , "_" , numOfCopies] = newCopy

    thereResponse["visited"] = True
    return charDictList, namelist


def parseAny(key, data, response, charDictList):
    if key not in charDictList:
        charDictList[key] = {}
    else:
        return charDictList, None
    namelist = []
    namelist.append(key)

    if key not in response:
        charDictList[key]["bio"] = ""
        charDictList[key]["type"] = key
        namelist.append(key)
        return charDictList, namelist

    anyResponse = response[key]


    if "visited" in anyResponse and anyResponse["visited"] == True or "hasTruthValue" in anyResponse and \
            anyResponse["hasTruthValue"] == False:
        return charDictList, None

    charDictList = parseRecursive(key, response, charDictList, key)
    return charDictList, namelist


def parseRecursive(key, response, charDictList, name):
    if key not in response:
        return charDictList
    if "hasQuality" in response[key]:
        for field in response[key]["hasQuality"]:
            if "descriptors" not in charDictList[name] or charDictList[name][
                "descriptors"] is None:
                charDictList[name]["descriptors"] = []
            charDictList[name]["descriptors"].append(field["value"])
    if "type" in response[key]:
        for field in response[key]["type"]:
            if key in field["value"]:
                continue
            else:
                charDictList = parseRecursive(field["value"], response, charDictList, name)
    if "subClassOf" in response[key]:
        for field in response[key]["subClassOf"]:
            if "Person" in field["value"] or "Organism" in field["value"] or "Location" in field[
                "value"] or "Information" in \
                    field["value"] or "Personification" in field["value"]:
                charDictList[name]["bio"] = field["value"]
                charDictList[name]["type"] = key
                return charDictList
            else:
                charDictList = parseRecursive(field["value"], response, charDictList, name)
    return charDictList


def parseSituations(data, response, charDictList):
    for key in response:
        if "situation_" in key and "visited" not in response[key]:
            charDictList, names = deepDive(key, response, charDictList, data)
    return charDictList


def parseTheres(data, response, charDictList):
    for key in response:
        if "there_" in key and "visited" not in response[key]:
            charDictList, names = deepDive(key, response, charDictList, data)
    return charDictList
