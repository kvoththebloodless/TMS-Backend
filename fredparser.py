#TODO: SUPPORT FOR BOXER patient example -he%20was%20growing%20mushrooms%20in%20the%20tree%20trunk%20and%20he%20wanted%20to%20have%20them%20for%20dinner

import requests
import utility as utility
import copy

from os import environ

# bearer = environ.get('FRED_API_TOKEN')
bearer = "API_TOKEN"
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
         "Topic", "Predicate", "Value", "Patient", "Product"]


def parse(data, charDictList, charinterface):
    params1.update({"text": data["line"]})

    response = requests.get(url=URL, params=params1, headers={"Accept": "application/rdf+json",
                                                              "Authorization": bearer})
    response = response.json()

    response = utility.formatFredResponse(response)
    print(data)
    # data=utility.extractAndAddHiddenVerbs(data,response)  # Puts 'GOAT' as a verb when doing "A lion walked across the grass to eat the goat"
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

        # if "visited" in response[verb] and response[verb]["visited"] == True:
        #
        #     continue
        #COMMENTING BECAUSE IF A VERB IS PART OF ANOTHER VERB THEN THE INNER VERB WHILE TRAVERSING THE FORMER VERB GETS SET TO VISITED AND THEN CAN'T
        #BE PRCESSED AGAIN AS A SEPERATE VERB "He wants an ice cream" has "have"hidden verb which is the theme for "want" node


        # response[verb]["visited"] = True
        if verb not in response:
            continue
        verbResponse = response[verb]

        animDict = {"name": verb[0:len(verb) - 2], "roles": {}}

        for key in verbResponse:

            # If Role
            if key in Roles:
                animDict["roles"][key] = []
                for field in verbResponse[key]:

                    charDictList, names = deepDive(field["value"], response, charDictList, data)
                    if names is not None and len(names) != 0:
                        animDict["roles"][key].extend(names)

            # Does Animation have a quality?
            if key == "hasQuality":
                animDict["quality"] = []
                for field in verbResponse[key]:
                    animDict["quality"].append(field["value"])

            # Is Animation attached to a quantity, for now we will assume it to be the number of times
            if key == "hasDataValue":
                animDict["repeat"] = []
                for field in verbResponse[key]:
                    animDict["repeat"] = field["value"]
            # is there a truth value associated with the animation
            if key == "hasTruthValue" and verbResponse[key][0]["value"] == "False": # Assuming only one truth value is inside. probably true.
                animDict["truthvalue"]="false"

        prep = utility.checkForPrepositionAfterVerb(data, verb,verbResponse)
        if prep is not None:
            animDict["prep_" + prep] = ""
            if prep in verbResponse:
                for field in verbResponse[prep]:
                    charDictList, names = deepDive(field["value"], response, charDictList, data)
                animDict["prep_" + prep] = names

        # Mark Node as visited and add animation to list

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

    prepkey = utility.checkForPrepositionInKeyNonv(situationResponse, key[0:len(key) - 2])

    if prepkey != None:
        for field in situationResponse[prepkey]:
            charDictList, names = deepDive(field["value"], response, charDictList, data)
            if names is not None and len(names) != 0:
                namelist.extend(names)
        for name in namelist:
            charDictList[name]["prep_" + prepkey] = names

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

    prepkey = utility.checkForPrepositionInKeyNonv(thereResponse, key[0:len(key) - 2])

    if prepkey != None:
        for field in thereResponse[prepkey]:
            charDictList, names = deepDive(field["value"], response, charDictList, data)
            if names is not None and len(names) != 0:
                namelist.extend(names)
        for name in namelist:
            charDictList[name]["prep_" + prepkey] = names
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

    namelist = []
    if key not in charDictList:
        charDictList[key] = {}

    namelist.append(
        key)  # this is for appearing in the animation section of the response sent back. Even if character is not to be
    # duplicated with another entry, the animation still needs to record a character in it's definition

    # else:
    #     return charDictList, None


    # if "visited" in response[key] and response[key]["visited"] == True or "hasTruthValue" in response[key] and \
    #         response[key]["hasTruthValue"] == False:
    #     return charDictList,None

    charDictList = parseRecursive(key, response, charDictList, key)
    # The following condition takes care of the condition when for eg. "Mary" is not in the response, which means no further categories.
    #     if key not in response:
    #         charDictList[key]["bio"] = "Person" #default bio
    #         charDictList[key]["type"] = key
    #         return charDictList, namelist
    #
    #     anyResponse = response[key]

    #     return charDictList, None

    # charDictList = parseRecursive(key, response, charDictList, key)
    if charDictList[key]=={}:
        del charDictList[key]
    return charDictList, namelist


def parseRecursive(key, response, charDictList, name):
    if key not in response:
        charDictList[name]["bio"] = "Uncatergorized"  # default bio
        charDictList[name]["type"] = key
        return charDictList
    if "visited" in response[key] and response[key]["visited"] == True or "hasTruthValue" in response[key] and \
            response[key]["hasTruthValue"] == False:
        return charDictList

    response[key]["visited"] = True

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
        for field in response[key]["subClassOf"]:  # desired subtypes
            if "Person" in field["value"] or "Organism" in field["value"] or "Location" in field[
                "value"] or "Information" in \
                    field["value"] or "Personification" in field["value"] or "Event" in field[
                "value"] or "PhysicalObject" in field["value"]:
                charDictList[name]["bio"] = field["value"]
                charDictList[name]["type"] = key
                return charDictList
            elif "Quality" in field["value"]:  # undesired subtypes, extend this list to add more
                del charDictList[name]
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
