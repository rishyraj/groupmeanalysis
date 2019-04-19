import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pickle
from datetime import datetime, timedelta, timezone, date

stopWords = set(stopwords.words('english'))
punctuation = set(['.',',','?','!','’',"\'","\'s",'@',':','(',')','%'])

data = ""

with open('message.json', encoding='utf-8') as f:
    data = json.load(f)

# Example of System Data
# {"attachments":[],"avatar_url":null,"created_at":1534094206,"favorited_by":[],"group_id":"42549431",
# "id":"153409420685189988","name":"GroupMe","sender_id":"system","sender_type":"system",
# "source_guid":"6a83889080810136b6ed22000b698c65","system":true,
# "text":"Dan Foley has joined the group","user_id":"system",
# "event":{"type":"membership.announce.joined","data":{"user":{"id":43054355,"nickname":"Dan Foley"}}}}

# Example of user data
# {'attachments': [], 'avatar_url': 'https://i.groupme.com/1022x1024.jpeg.c99eabb4edd64e50be39b03a87766afe', 'created_at': 1555261657, 
#     'favorited_by': ['25032862', '62590867'], 'group_id': '42549431', 
#     'id': '155526165735503974', 'name': 'Will Baker', 'sender_id': '45231839', 
#     'sender_type': 'user', 'source_guid': '16B4314B-BF54-4B2E-9F6D-69328BF7EA71', 
#     'system': False, 
#     'text': 'https://purdue.ca1.qualtrics.com/jfe/form/SV_3kmvDl2Fpx5G3FH\n\nYou’ll receive a lifetime of happiness taking this especially because it is only multiple choice questions in simple form.', 
#     'user_id': '45231839', 'platform': 'gm'}

# How to handle unix epoch time
# timeExample = data[len(data)-1]["created_at"]
# utc_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timeExample)
# print(utc_time.date())

def getPersonData(name,data):
    idToName = userIdToName(data)
    if (isValidUser(name,idToName)==False):
        print("NameNotFoundError: This person was not in the group chat.")
        return "Error"   
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

def getTimeData(data):
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

def getGeneralDayData(data,date):
    wordDict = {}
    texts = []
    for messages in data:
        timeStamp = messages["created_at"]
        utc_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timeStamp)
        utc_time = utc_time.date()
        if (utc_time==date):
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

def getPersonDayData(name,data,date):
    idToName = userIdToName(data)
    if (isValidUser(name,idToName)==False):
        print("NameNotFoundError: This person was not in the group chat.")
        return "Error"   
    wordDict = {}
    texts = []
    for messages in data:
        timeStamp = messages["created_at"]
        utc_time = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timeStamp)
        utc_time = utc_time.date()
        if (messages["name"]==name and utc_time==date):
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

def userIdToName(data):
    idToName = {}
    nameToId = {}
    for i in range(len(data)-1,-1,-1):
        messages = data[i]
    # for messages in data:
        try:
            if (messages["user_id"]=="system"):
                # print(messages["event"]["type"])
                if ("changed name" in messages["text"]):
                    indx = -1
                    text = messages["text"]
                    text = text.replace(" changed name",'')
                    for word in text.split():
                        if (word=="to"):
                            break
                        else:
                            indx+=len(word)
                        indx+=1
                    origName = text[0:indx]
                    origId = nameToId[origName]
                    newName = text[indx+4:len(text)]
                    newId = origId
                    idToName[newId]=newName
                    nameToId[newName]=newId
                    continue
                if (messages["event"]["type"]=="membership.announce.joined" or messages["event"]["type"]=="membership.announce.added"):
                    if (messages["event"]["type"]=="membership.announce.joined"):
                        id = str(messages["event"]["data"]["user"]["id"])
                        name = messages["event"]["data"]["user"]["nickname"]
                        idToName[id]=name
                        nameToId[name]=id
                    else:
                        for user in messages["event"]["data"]["added_users"]:
                            id = str(user["id"])
                            name = user["nickname"]
                            idToName[id]=name
                            nameToId[name]=id
        except:
            continue
    # print(idToName)
    return idToName
    # for messages in data:
    #     valueSet = set(idToName.values())
    #     if (messages["name"]!="GroupMe"):
    #         if(messages["name"] not in valueSet):
    #             idToName[messages["user_id"]]=messages["name"]
    #         else:
    #             continue
    # return idToName

def isValidUser(name,idToName):
    names = set(idToName.values())
    return (name in names)

def mostCommon(n,words):
    ordered = sorted(words.items(), key=lambda x:x[1],reverse=True)
    if (n>len(ordered)):
        print("n value is over the list of words said, changing n from",n,"to",len(ordered))
        n=len(ordered)
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

def plotTimeData(timeData,beginningDate=False,endDate=False):
    dates = timeData[0]
    messagesSent = timeData[1]
    if (beginningDate==False and endDate==False):
        plt.plot_date(x=dates,y=messagesSent, fmt="r-")
        plt.xticks(np.arange(0,len(dates),20))
        plt.show()
    else:
        if (isinstance(beginningDate,date)==False or isinstance(endDate,date)==False):
            print("TypeError: The format of the given date is wrong, make sure that the dates are instances of datetime.date")
            return "Error"
        try:
            begIndx = dates.index(str(beginningDate))
            endIndx = dates.index(str(endDate))
            if (begIndx > endIndx):
                userInpt = input("FormatError: endDate is before beginningDate, would you like to switch the two dates?\n")
                userInpt = userInpt.lower()
                if (userInpt=="yes"):
                    temp = begIndx
                    begIndx=endIndx
                    endIndx=temp
                else:
                    print("This funtion is now exiting...")
                    return "Error"
            if (begIndx == endIndx):
                print("FormatError: make sure that beginningDate is not the same as endDate, there needs to be at least a day separation")
                return "Error"
            newDates = []
            newMsg = []
            for i in range(begIndx,endIndx+1):
                newDates.append(dates[i])
                newMsg.append(messagesSent[i])
            plt.plot_date(x=newDates,y=newMsg,fmt="r-")
            delta = endIndx-begIndx
            modifier = int(delta/20) + 2
            if (modifier == 0):
                modifier = 3
            if (delta < 12):
                modifier = 1
            plt.xticks(np.arange(0,len(newDates),modifier))
            plt.show()
        except ValueError:
            print("OutOfBoundsError: This date is outside the range of the lifespan of this group chat, make sure your dates fall within the range of the group chat lifespan")
        except:
            print("An Error Occured.")

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

def getUserActivityRank(data,idToName):
    userLst = idToName.values()
    keySet = 0
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
    for user in userLst:
        if (user not in keySet):
            persons[user]=0
    ordered = sorted(persons.items(), key=lambda x:x[1],reverse=True)
    # print(ordered)
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

def lookupUserActivityStats(person,users,idToName):
    if (isValidUser(person,idToName)==False):
        print("NameNotFoundError: This person was not in the group chat.")
        return "Error"
    count = 0
    messageCt = messagesSentCount(users)
    for user in users:
        count+=1
        if (user[0]==person):
            print(person,"has sent",user[1],"messages")
            print(person,"has an activity rank of",count,"out of",len(users),"users")
            print(person,"has sent",str(float(user[1]/messageCt)*100),"percent of all messages in this group chat")
            return count

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
idToName =userIdToName(data)
# timeData = getTimeData(data)
# plotTimeData(timeData)
# words_gen = loadPickleData('H3N.pickle')
# words_gen_day = getGeneralDayData(data,date(year=2018,month=12,day=4))
# words_per = getPersonData("Phillip Archuleta", data)
# words_per_day = getPersonDayData("Phillip Archuleta",data,date(year=2018,month=12,day=4))
# print(words_per_day)
# wordConcentration(words_per,words_gen,"balloons")
# mostPopular = getUserFavoriteStats(data)
# print(userIdToName(data))
# fanLst = getFans("Gary Chen", data)
# rankedLst = rankedFans(5,fanLst)
# mostPopular = getUserFavoriteStats(data)
# mostFavoriter = getFavoriterStats(data)
# mostCommon(10,words_per_day)
# wordRange(80,90,mostPopular)
# lookupWord("purdue",words)
# users = getUserActivityRank(data,idToName)
# activeUsers = getMostActiveUsers(users,5)
# activeUsers = getActiveUsersRange(10,20,users)
# rank = lookupUserActivityStats("Dan Foley",users,idToName)
# rankedUser = reverseLookup(len(users)-5,users)