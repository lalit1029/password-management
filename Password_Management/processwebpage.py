from databasev2 import database
from urllib import request
import string
import re
import fileinput
import json


class ProcessWebpage:
    def __init__(self, HTMLContent):
        self.HTMLContent= HTMLContent
        self.indexedhtml=dict()

    def SearchHTML(self):
        db2=database(filename= "C:/Python_Files\Password_Management/Application/HTMLindexing", table="Indexpage")
        db2.connect_database()
        query = 'drop table if exists Indexpage'
        db2.sql_noparam(query)
        Tagsname= "(?P<tagname>(?<=\<)\w+)"
        Tagsboundary="(<\tagname.*?[(\>)|(</\tagname>)])"
        testhtml= "<html><head><link rel='shortcut icon' href='#' /></head><body><div id=1234><p style='bold'>This is default response from server</p></div><div></div></body></html>"
        tagparams={}
        indexedhtml={}
        try:
            Tagsnamere =re.finditer(Tagsname,str(self.HTMLContent["Default"]),re.DOTALL)
        except AttributeError as e:
            print("Error parsing HTML:{}".format(e))
        scriptcount=0
        scriptcheck=0
        for Tags in Tagsnamere:
            if scriptcheck==1  and Tags.start()< scriptoffset and Tags.groups()[0]!="script":
                continue
            elif scriptcheck==1 and Tags.start() > scriptoffset and Tags.groups()[0]!="script":
                scriptcheck==0
                scriptoffset=0
            Tagsattributes="(\<" + Tags.groups()[0] +"(\s+(?P<attributename>[a-zA-Z0-9_-]+?)=(?P<attrbutevalue>.*?))*?\s?\/?\>)"
            Tagattributes= "(?P<tagattributes>\<"+Tags.groups()[0]+".*?(\>))"
            Tagsboundary= "(?is)(?P<tagboundary>\<"+Tags.groups()[0]+".*?\>.*?(\<\/"+Tags.groups()[0]+"\>))"
            Tagsboundary2="(?P<tagboundary>\s*?\<" + Tags.groups()[0]+".*?(\/\>))"
            Tagsboundary3="(?is)(?P<tagboundary>\<"+Tags.groups()[0]+".*?\>.*)"
            javascriptids="^(?P<javascript>\<(script).*?\>.*?\<\/\2\>)"
            try:
                TagsboundarySearch=re.search(Tagsboundary,self.HTMLContent["Default"][Tags.start()-1:],re.DOTALL)
            except AttributeError as e:
                print("Tag Boundary not Found:".format(e))
                pass
            if TagsboundarySearch!=None:
                check="Long"
                try:
                    TagsattributesSearch=re.search(Tagsattributes,TagsboundarySearch.groups()[0],re.DOTALL)
                except AttributeError as e:
                    print("Error attribute not forund:{}".format(e))
                    pass
                if Tags.groups()[0]=="script" or Tags.groups()[0]=="SCRIPT":
                    scriptcheck=1
                    scriptoffset=(Tags.start()-1) + len(TagsboundarySearch.groups()[0])
            elif (TagsboundarySearch==None and re.search(Tagsboundary2,self.HTMLContent["Default"][Tags.start()-1:],re.DOTALL) != None):
                try:
                    Tagsboundary2Search = re.search("(?P<tagboundary>\s*?\<" + Tags.groups()[0] + ".*?(\/\>))", self.HTMLContent["Default"][Tags.start() - 1:], re.DOTALL)
                except AttributeError as e:
                    print("Attribute Error:{}".format(e))
                    pass                 
                check="Short"
            else:
                TagsboundarySearch= re.search(Tagsboundary3,self.HTMLContent["Default"][Tags.start()-1:],re.DOTALL)
                check="Long"
            if(check=="Long"):
                Tagattributes2='\s+'
                try:
                    TagsattributesSplit1=re.split(Tagattributes2,TagsattributesSearch.groups()[0])
                except AttributeError as e:
                    print("Error parsing:{}".format(e))
                    pass
                TagsattributesSplit2=[]
                TagsattributesSplit3=[[],[]]
                i=1
                while(i<=(len(TagsattributesSplit1)-1)):
                    TagsattributesSplit2=re.split(r"\=",TagsattributesSplit1[i].strip('["\'/>]'))
                    if(TagsattributesSplit2!=None):
                        TagsattributesSplit3[0].append(TagsattributesSplit2)
                    else:
                        i+=1
                        continue
                    i+=1
                TagsattributesSplit3[1].append(TagsboundarySearch.groups(1)[0])
            else:
                TagsattributesSearch=re.search(Tagsattributes,Tagsboundary2Search.groups()[0][Tagsboundary2Search.start():],re.DOTALL)
                Tagattributes2='(?P<attributename>(\w\d_-)*)\=(?<attributevalue>(\w\d_-\\\/\.\?)*)'
                Tagattributes2='\s+'
                TagsattributesSplit1=re.split(Tagattributes2,TagsattributesSearch.groups()[0])
                TagsattributesSplit2=[]
                TagsattributesSplit3=[[],[]]
                i=1
                while(i<=(len(TagsattributesSplit1)-1)):
                    TagsattributesSplit2=re.split(r"\=",str(TagsattributesSplit1[i]),re.DEBUG)
                    if(TagsattributesSplit2!=None):
                        TagsattributesSplit3[0].append(TagsattributesSplit2)
                    else:
                        continue
                    i+=1
                TagsattributesSplit3[1].append(Tagsboundary2Search.groups()[0])
            self.indexedhtml[(Tags.groups()[0]+str(Tags.start())+ "-" + str(Tags.end()))]=TagsattributesSplit3
            check=None
        return self.indexedhtml
        
    def UpdateHTMLContent(self, params):
            num=1
            span=[0,0]
            tag=""
            for c in params["Tags"]:
                    if ((ord(c)>=97 and ord(c)<=122) or (ord(c) >= 65 and ord(c) <= 90)):
                        tag+=c
                    elif((ord(c)>= 48 and ord(c)<= 57) and num==1):
                        span[0]=(span[0]*10)+int(c)
                    elif(c=='-'):
                        num=2
                    elif((ord(c)>= 48 and ord(c)<= 57) and num==2):
                        span[1]=(span[1]*10) + int(c)
                    else:
                        break
            indexedhtml= self.SearchHTML()
            tagboundaryinitial= len(indexedhtml[params["Tags"]][1])
            updatedattributes=""
            attributestring=""
            for keys in params:
                match keys:
                    case "attributename":
                        if(params["attributename"]==None):
                            continue
                        i=0
                        check=0
                        for attributes in indexedhtml[params["Tags"]][0]:
                            if(attributes[0]==params["attributename"]):
                                indexedhtml["Tags"][0][i][1]=params["attributevalue"]
                                check=1
                                break
                            else: check==0
                            i+=1
                        if check==0:
                            indexedhtml[params["Tags"]][0].append([params["attributename"],params["attributevalue"]])
                        for attribute in indexedhtml[params["Tags"]][0]:
                            if(len(attribute)==2):
                                attributestring+= attribute[0] + "=" + '"' + attribute[1] + '" '
                        updatedattributes= "<" + tag + " " + attributestring + "/>"
                        break
                    case "attributevalue":
                        if(params["attributename"]==None):
                            continue
                        break
                    case "tagcontent":
                        if params["tagcontent"]!= None:
                            indexedhtml[params["Tags"]][1][0]=indexedhtml[params["Tags"]][1][0][:params["tagcontentoffset"]] + params["tagcontent"] + indexedhtml[params["Tags"]][1][0][params["tagcontentoffset"]:] 
                        break
                    case "javascript":
                        if params["javascirpt"]!= None:
                            indexedhtml[params["Tags"]][1][0]=indexedhtml[params["Tags"]][1][0][:params["scriptoffset"]] + params["javascript"] + indexedhtml[params["Tags"]][1][0][params["scriptoffset"]:]
                        break
                    case default:
                        continue
            self.HTMLContent["Updated"]= self.HTMLContent["Default"][:span[0]-1]
            if(params["attributename"]!=None):
                self.HTMLContent["Updated"]+=updatedattributes 
            if(params["tagcontent"]!=None or params["javascript"]!=None):
                self.HTMLContent["Updated"]+= indexedhtml[params["Tags"]][1][0] + self.HTMLContent["Default"][(span[0]-1) +len(indexedhtml[params["Tags"]][1][0])- len("tagcontent"):]
            if(params["attributename"]!=None and (params["tagcontent"]!=None or params["javascript"]!=None)):
                self.HTMLContent["Updated"]= self.HTMLContent["Updated"] + self.HTMLContent["Default"][span[0] + len(updatedattributes) - len(params["attributename"] + params["attributevalue"]):]
            return self.HTMLContent["Updated"]
            
##def main():
##    wfile={"Default":"", "Updated":""}
####    with fileinput.input(files='C:/Python_Files/Password_Management/Application/HTML/index.html',mode='r') as input:
####                for line in input:
####                    wfile["Default"]+=line
##    req=request.Request(url="https://wipro.com",method="GET")
##    resp=request.urlopen(req)
##    wfile["Default"]=str(resp.read())
##    indexedhtml=ProcessWebpage(wfile)
##    indexedhtmlcontent=indexedhtml.SearchHTML()
##    for keys in indexedhtmlcontent:
##        print("Keys:{}  Tagattributes: {}    Tagboundary: {}".format(keys,indexedhtmlcontent[keys][0], indexedhtmlcontent[keys][1]))
##    #except error.HTTPError as e:
##    #    print(e.fp.read(),e.code)
##    print("Original Web content:" + wfile["Default"])
##    #provide htmlparamter index to be updated 
##    print(indexedhtml.UpdateHTMLContent({"Tags": "body341-345" ,"attributename" : None, "attributevalue": None,"tagcontent": "<br>This is inserted text!!!</br>", "tagcontentoffset":21 , "javascript": None, "javascriptoffset":None}))
##     
##if __name__=="__main__":main()
