import fredparser as fred
import mongointerface as mongo
import characterinterface as charinterface
import animationinterface as animinterface
import ruleparser as rm
import utility as ut
from pymongo import MongoClient


'''
return the instance of the character interface
'''
def getCharInstance():
    return  charinterface

'''
return the instance of the animation interface
'''
def getAnimInstance():
    return animinterface

'''
parse the text and retrieve the character dictionaries and the animation sequences
'''
def parse(data,charDictList,db):
    animDictList,newCharDictList=rm.match(data,db)
    if newCharDictList==None or animDictList==None or (len(newCharDictList)==0 and len(animDictList)==0):
        newCharDictList,animDictList=fred.parse(data,charDictList,None)
    return {"characters":newCharDictList,"animations":animDictList}

