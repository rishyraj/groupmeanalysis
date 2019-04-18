import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pickle
import sys
from datetime import datetime, timedelta, timezone, date

stopWords = set(stopwords.words('english'))
punctuation = set(['.',',','?','!','’',"\'","\'s",'@',':','(',')','%'])

data = ""

with open('message.json', encoding='utf-8') as f:
    data = json.load(f)

# Example of data
# {'attachments': [], 'avatar_url': 'https://i.groupme.com/1022x1024.jpeg.c99eabb4edd64e50be39b03a87766afe', 'created_at': 1555261657, 
#     'favorited_by': ['25032862', '62590867'], 'group_id': '42549431', 
#     'id': '155526165735503974', 'name': 'Will Baker', 'sender_id': '45231839', 
#     'sender_type': 'user', 'source_guid': '16B4314B-BF54-4B2E-9F6D-69328BF7EA71', 
#     'system': False, 
#     'text': 'https://purdue.ca1.qualtrics.com/jfe/form/SV_3kmvDl2Fpx5G3FH\n\nYou’ll receive a lifetime of happiness taking this especially because it is only multiple choice questions in simple form.', 
#     'user_id': '45231839', 'platform': 'gm'}


def getPersonData(name,data):
    wordDict = {}
    texts = []
    for messages in data:
        if (messages["name"]==name):
            texts.append(messages["text"])
    for t in texts:
        if (isinstance(t,str)):
            t = t.lower()
        else:
            continue
        tokenized_sent = word_tokenize(t)
        for w in tokenized_sent:
            keySet = set(wordDict.keys())
            if (w not in stopWords) and (w not in punctuation):
                if (w not in keySet):
                    wordDict[w]=1
                else:
                    wordDict[w]+=1
    return wordDict

def getGeneralData(data):
    wordDict = {}
    texts = []
    for messages in data:
        texts.append(messages["text"])
    for t in texts:
        if (isinstance(t,str)):
            t = t.lower()
        else:
            continue
        tokenized_sent = word_tokenize(t)
        for w in tokenized_sent:
            keySet = set(wordDict.keys())
            if (w not in stopWords) and (w not in punctuation):
                if (w not in keySet):
                    wordDict[w]=1
                else:
                    wordDict[w]+=1
    return wordDict

# How to handle unix epoch time
# timeExample = data[len(data)-1]["created_at"]
# utc_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timeExample)
# print(utc_time.date())

def getTimeData(data):
    # d1 = date(2019,3,31)
    # d2 = date(2019,4,12)
    # tpLbl = []
    # tpLbl.append(d1)
    # temp = []
    # temp.append(12)
    # dt = d2-d1
    # ctr=1
    # while(dt.days>1):
    #     newDate = d1+timedelta(days=ctr)
    #     ctr+=1
    #     tpLbl.append(newDate)
    #     temp.append(0)
    #     dt = d2-newDate
    # tpLbl.append(d2)
    # temp.append(23)
    # print(tpLbl)
    # print(temp)
    # sys.exit()
    labels = []
    messagesSentPerDay = []
    ct = 0
    msgCt = 0
    for i in range(len(data)-1,0,-1):
        # print(i)
        # if (i<len(data)-10): break
        message = data[i]
        timeStamp = message["created_at"]
        utc_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timeStamp)
        utc_time = utc_time.date()
        stRep = set(labels)
        if (utc_time not in stRep):
            # print("add")
            if (i!=len(data)-1):
                # print("hit")
                # print(len(labels))
                # print(ct)
                dt = utc_time-labels[ct-1]
                # print(dt)
                ctr=1
                while(dt.days>1):
                    newDate = labels[ct-1]+timedelta(days=ctr)
                    # print(newDate)
                    ctr+=1
                    labels.append(newDate)
                    # ct = len(labels)
                    messagesSentPerDay.append(0)
                    dt = utc_time-newDate
                messagesSentPerDay.append(msgCt)
            labels.append(utc_time)
            msgCt=0
        ct=len(labels)
        # print(labels)
        msgCt+=1
    messagesSentPerDay.append(msgCt)
    for i in range(len(labels)):
        labels[i] = str(labels[i])
    # print(len(labels))
    # print(len(messagesSentPerDay))
    return (labels,messagesSentPerDay)

def mostCommon(n,words):
    ordered = sorted(words.items(), key=lambda x:x[1],reverse=True)
    x=np.arange(n)
    x_ticks = []
    y_val = []
    for i in range(n):
        x_ticks.append(ordered[i][0])
        y_val.append(ordered[i][1])
    plt.bar(x,y_val)
    plt.xticks(x,x_ticks)
    plt.xticks(fontsize=6,rotation=30)
    plt.show()

def wordRange(low,high,words):
    ordered = sorted(words.items(), key=lambda x:x[1],reverse=True)
    num = high - low + 1
    x=np.arange(num)
    x_ticks = []
    y_val = []
    for i in range(low,(high+1)):
        x_ticks.append(ordered[i][0])
        y_val.append(ordered[i][1])
    plt.bar(x,y_val)
    plt.xticks(x,x_ticks)
    plt.xticks(fontsize=6,rotation=30)
    plt.show()

def lookupWord(tag,words):
    try:
        print("The word",tag,"appears",words[tag],"times")
        ordered = sorted(words.items(), key=lambda x:x[1],reverse=True)
        ctr=0
        for o in ordered:
            ctr+=1
            if (o[0]==tag):
                print("The word rank is",ctr)
                break
        return words[tag]
    except:
        print("This word doesn't exist or wasn't counted because it's a useless word")
        return False
def wordConcentration(personData,genData,tag):
    personCt = lookupWord(tag,personData)
    genCt = lookupWord(tag,genData)
    if (genCt==False):
        print("=======")
        print("Sorry, cannot get stats. Try a different word.")
        print("=======")
    else:
        ratio = personCt/genCt
        print("=======")
        print("This person contributed to",str(float(ratio*100)),"percent of the occurences of",tag)
        print("=======")

def plotTimeData(timeData):
    dates = timeData[0]
    messagesSent = timeData[1]
    plt.plot_date(x=dates,y=messagesSent, fmt="r-")
    plt.xticks(np.arange(0,len(dates),20))
    plt.show()
    
def getUserFavoriteStats(data):
    persons = {}
    for messages in data:
        keySet = set(persons.keys())
        if (messages["name"]!="GroupMe"):
            if (messages["name"] not in keySet):
                persons[messages["name"]]=len(messages["favorited_by"])
            else:
                persons[messages["name"]]+=len(messages["favorited_by"])
        else:
            continue
    return persons

def getFavoriterStats(data):
    persons = {}
    idToName = userIdToName(data)
    nameLst = idToName.keys()
    keySet = ""
    for messages in data:
        keySet = set(persons.keys())
        if (messages["name"]!="GroupMe"):
            for id in messages["favorited_by"]:
                try:
                    name = idToName[str(id)]
                    if (name not in keySet):
                        persons[name]=1
                    else:
                        persons[name]+=1
                except:
                    continue
        else:
            continue
    for n in nameLst:
        if (n not in keySet):
            persons[n]=0
    return persons

def getFans(name,data):
    fans = {}
    idToName = userIdToName(data)
    for messages in data:
        keySet = set(fans.keys())
        if (messages["name"]==name):
            fav = messages["favorited_by"]
            for f in fav:
                try:
                    nm = idToName[str(f)]
                    if (nm not in keySet):
                        fans[nm]=1
                    else:
                        fans[nm]+=1
                except:
                    continue
    ordered = sorted(fans.items(), key=lambda x:x[1],reverse=True)
    return ordered

def rankedFans(n,fans):
    if (n>len(fans)):
        print("The passed in value is greater than the list of fans, reducing value from",n,"to",len(fans))
        n = len(fans)
    rankedFans = []
    x=np.arange(n)
    x_ticks = []
    y_val = []
    print("====The top",n,'people that have liked this person\'s messages====')
    for i in range(n):
        rankedFans.append(fans[i])
        x_ticks.append(fans[i][0])
        y_val.append(fans[i][1])
        print(str(str(i+1)+"."),fans[i][0],"with",fans[i][1],"hearts given")
    print("====================================")
    plt.bar(x,y_val)
    plt.xticks(x,x_ticks)
    plt.xticks(fontsize=6,rotation=30)
    plt.show()
    return rankedFans

def userIdToName(data):
    idToName = {}
    for messages in data:
        valueSet = set(idToName.values())
        if (messages["name"]!="GroupMe"):
            if(messages["name"] not in valueSet):
                idToName[messages["user_id"]]=messages["name"]
            else:
                continue
    return idToName

def getUserActivityRank(data):
    persons = {}
    for messages in data:
        keySet = set(persons.keys())
        if (messages["name"]!="GroupMe"):
            if (messages["name"] not in keySet):
                persons[messages["name"]]=1
            else:
                persons[messages["name"]]+=1
        else:
            continue
    ordered = sorted(persons.items(), key=lambda x:x[1],reverse=True)
    return ordered

def getMostActiveUsers(persons,n):
    activeUsers = []
    x=np.arange(n)
    x_ticks = []
    y_val = []
    messageCt = messagesSentCount(persons)
    print("The",n,"Most Active Users")
    print("=================")
    for i in range(n):
        tup = persons[i]
        print(str(str(i+1)+"."),"User Name:",tup[0],"| Messages Sent:",tup[1],"| Contribution Percentage:",str(float(tup[1]/messageCt)*100),"%")
        x_ticks.append(tup[0])
        y_val.append(tup[1])
        activeUsers.append(tup)
    print("================")
    plt.bar(x,y_val)
    plt.xticks(x,x_ticks)
    plt.xticks(fontsize=6,rotation=30)
    plt.show()
    return activeUsers

def getActiveUsersRange(low,high,persons):
    activeUsers = []
    num = high - low + 1
    x=np.arange(num)
    x_ticks = []
    y_val = []
    messageCt = messagesSentCount(persons)
    print("Active Users from ranks",low,"to",high)
    print("=================")
    for i in range((low-1),(high)):
        tup = persons[i]
        print(str(str(i+1)+"."),"User Name:",tup[0],"| Messages Sent:",tup[1],"| Contribution Percentage:",str(float(tup[1]/messageCt)*100),"%")
        x_ticks.append(tup[0])
        y_val.append(tup[1])
        activeUsers.append(tup)
    print("================")
    plt.bar(x,y_val)
    plt.xticks(x,x_ticks)
    plt.xticks(fontsize=6,rotation=30)
    # plt.setp(labels)
    plt.show() 
    return activeUsers

def lookupUserActivityStats(person,users):
    count = 0
    messageCt = messagesSentCount(users)
    for user in users:
        count+=1
        if (user[0]==person):
            print(person,"has sent",user[1],"messages")
            print(person,"has an activity rank of",count,"out of",len(users),"users")
            print(person,"has sent",str(float(user[1]/messageCt)*100),"percent of all messages in this group chat")
            return count
    return "This User Does Not Exist in the Group Chat"

def reverseLookup(n,users):
    try:
        user = users[n-1]
        print(str(str(n)+"."),"User Name:",user[0],"| Messages Sent:",user[1])
        return user[1]
    except:
        print("You have entered in a value that is beyond the number of users in this group chat")
        return "error"

def messagesSentCount(users):
    count=0
    for user in users:
        count+=user[1]
    return count

def pickleData(filename,words):
    fn = filename+'.pickle'
    file = open(fn,'wb')
    pickle.dump(words,file, protocol=pickle.HIGHEST_PROTOCOL)
    file.close()
def loadPickleData(filepath):
    file = open(filepath,'rb')
    data = pickle.load(file)
    file.close()
    return data


#=======================================================================================================================
# diff = data[0]["created_at"]-data[len(data)-1]["created_at"]
# print(diff)
timeData = getTimeData(data)
plotTimeData(timeData)
# words_gen = loadPickleData('H3N.pickle')
# words_per = getPersonData("Phillip Archuleta", data)
# wordConcentration(words_per,words_gen,"balloons")
# mostPopular = getUserFavoriteStats(data)
# print(userIdToName(data))
# fanLst = getFans("Gary Chen", data)
# rankedLst = rankedFans(5,fanLst)
# mostPopular = getUserFavoriteStats(data)
# mostFavoriter = getFavoriterStats(data)
# mostCommon(10,mostPopular)
# wordRange(80,90,mostPopular)
# lookupWord("purdue",words)
# users = getUserActivityRank(data)
# activeUsers = getMostActiveUsers(users,5)
# activeUsers = getActiveUsersRange(10,20,users)
# rank = lookupUserActivityStats("Gary Chen",users)
# rankedUser = reverseLookup(len(users)-5,users)