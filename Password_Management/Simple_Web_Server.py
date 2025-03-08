'''
        Application Name: Password Manager Application
        Created By: Lalit Jagotra
'''
import http.server
import socketserver
import http.client
from urllib import request
import os
import fileinput
import string
import re
import hashlib
import hmac
from databasev2 import database
from processwebpage import ProcessWebpage
import processwebpage
import socket
from urllib import parse
from datetime import timedelta  
from datetime import datetime
import secrets
from Crypto.Cipher  import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
import getpass
import binascii
import base64

PORT =8000        
class CustomViews():
    def __init__(self,htmlpage={"Default":"template1","Updated":""},updateparams=""):
        self.htmlpage=dict()    
        self.htmlpage=htmlpage
        self.updateparams=updateparams
        self.appdir=os.getcwd()

    def AddForm(self,htmlform):
        updatecontent= "<form action="+ htmlform['form']['action'] + " method=" + htmlform['form']['method']+ "><fieldset>"
        for input in htmlform["fields"]:
            updatecontent+="<br><label for=" + input['name'] + "></label><input type=" + input['type'] + " name=" + input['name'] + " value=''" + " placeholder=" + input['placeholder'] + " /></br>"
        updatecontent+= "<br><input type='submit'></br></fieldset></form>"
        self.updateparams={"Tags":"div1180-1183","tagcontentoffset":28, "tagcontent": updatecontent, "attributename":None, "attributevalue":None} 
        return self.customview()
  
    def customview(self):
        if self.htmlpage["Default"].startswith("template"):
            template=self.htmlpage["Default"]
            self.htmlpage["Default"]=""
            with fileinput.input(files=self.appdir + "\\Application\\HTML\\"+ template + ".html",mode="r") as input:
                for line in input:
                    self.htmlpage["Default"]+=line
        pageupdate1=ProcessWebpage(self.htmlpage)
        self.htmlpage["Updated"]= pageupdate1.UpdateHTMLContent(self.updateparams)
        return self.htmlpage
        
        
class datamodel():
    def __init__(self,**dataargs):
        self.dataparams={"datasource":{"database":{"databasename":str(None),"tablename":str(None)},"requestquerystring":{},"websource":{"url":None,"parameters":[{"Tags":None,"attributename":None,"tagcontent":None,"tagcontentoffset":None}]}}}	
        return
    
    def retrievedata(self):
        args=dict()
        for keys in self.dataparams["datasource"]:
            if keys=="requestquerystring":
                if self.dataparams["datasource"][keys]==None:
                    break
                args[keys]= self.dataparams["datasource"]["requestquerystring"]
                argslen=len(args[keys]["action"]) + len(args[keys]["number"])
                argsstring= args[keys]["action"] +args[keys]["number"]
            elif keys== "database":
                if self.dataparams["datasource"][keys]["databasename"]==None:
                    continue
                args["Database"]=self.databaseconnect(self.dataparams["datasource"][keys]["databasename"], self.dataparams["datasource"][keys]["tablename"])  
            elif keys== "websource":
                if self.dataparams["datasource"][keys]["url"]==None:
                    continue
                webreq= request.Request(url=self.dataparams["datasource"][keys]["url"],method="GET")
                try:
                    webresp=request.urlopen(webreq)
                except error.HTTPError as e:
                    print(e.fp.read(),e.code)
                wfile={"Default":"", "Updated":""}
                wfile["Default"]=ascii(webresp.read())
                indexedhtmlobj=ProcessWebpage(wfile)
                indexedhtmlcontent=indexedhtmlobj.SearchHTML()
                i=0
                while(i<len(self.dataparams["datasource"][keys]["parameters"])):
                    if self.dataparams["datasource"][keys]["parameters"][i]["attributename"]!=None:
                        for j in range(0, len(indexedhtmlcontent[self.dataparams["datasource"]["websource"]["parameters"][i]["Tags"]][0])):
                            if indexedhtmlcontent[self.dataparams["datasource"]["websource"]["parameters"][i]["Tags"]][0][j][0]==self.dataparams["datasource"][keys]["parameters"][i]["attributename"]:
                                #print("Websource data param value:{}".format(indexedhtmlcontent[self.dataparams["datasource"][keys]["parameters"][i]["Tags"]][0][j][1]))
                                args[self.dataparams["datasource"][keys]["parameters"][i]["attributename"]]=indexedhtmlcontent[self.dataparams["datasource"][keys]["parameters"][i]["Tags"]][0][j][1]
                    if self.dataparams["datasource"][keys]["parameters"][i]["tagcontent"] !=None:
                        args["tagcontent"]=indexedhtmlcontent[self.dataparams["datasource"][keys]["parameters"][i]["tagcontent"]][1][0]
                    i+=1
            elif keys == "web-api":
                if self.dataparams["datasource"][keys]["url"]==None:
                    continue
                self.dataparams["datasource"][keys]["api-key"]
                match(self.dataparams["datsource"][keys]["api-auth"]):
                    case "querystring":
                        self.dataparams["datasource"][keys]["url"]+"&" + (self.dataparams["datasource"][keys]["authparamname"] + '=' + self.dataparams["datasource"][keys]["api-secret"])
                    case "autorization-send-secret":
                        self.dataparams["datasource"][keys]["authheader"]=self.dataparams["datasource"][keys]["authparamname"] + '=' + self.dataparams["datasource"][keys]["api-secret"]
                    case "authoirzation-req-sign":
                        HashedPayload= hashlib.new("sha256")
                        HashedPayload.update(b'')
                        canonicalString= bin(self.dataparams["datasource"][keys]["canonicalstring"])
                        HashedCanonicalRequest = hashlib.new("sha256")
                        HashedCanonicalRequest.update(canonicalString)
                        SignatureString =bin(self.dataparams["datasource"][keys]["signaturestring"]) + HashedCanonicalRequest.digest()
                        HashedSignatureString= hmac.new(self.dataparams["datasource"][keys]["api-secret"],SignatureString,digestmod="sha256")
                        Headers=self.dataparams["datasource"][keys]["authheader"] + self.dataparams["datasource"][keys]["authparamname"] + '=' + HashedSignatureString
        return args
    
    def databaseconnect(self,database1, table1):
        db1=database(filename= database1, table=table1)
        db1.connect_database()
        count = db1.countrecs()
        return db1.retrieve_rows()

class HTTPRequestClass(http.server.BaseHTTPRequestHandler):
    usersession=dict(dict())
    authenticateduser=list()
    currentuser=str()
    usertabledb= str()
    masterpass=str()
    appdir=os.getcwd()
    dbadminpwd=str()
    def index(self,args):
            wfile={"Default":"","Updated":""}
            with fileinput.input(files=self.appdir+ '\\Application\\HTML\\index.html',mode='r') as input:
                for line in input:
                    wfile["Default"]+=line
            addss=str()
            with fileinput.input(files=self.appdir + '\\Application\\HTML\\main.css',mode='r') as input:
                for line in input:
                    addss+=line
            updateparams={"Tags": "html1-5" ,"attributename" : None, "attributevalue": None,"tagcontent": addss, "tagcontentoffset":62 , "javascript": None, "javascriptoffset":None}
            addstylesheet=CustomViews(wfile,updateparams)
            addstylesheet.customview()
            wfile["Default"]=addstylesheet.htmlpage["Updated"]
            if (args["action"]==None):
                self.send_response(code= 200,message='OK')
                self.send_header("ServerName","Server1")
                self.send_header("Pragma","No-Cache\r\n\n"+wfile["Default"])   
                self.end_headers()
            index=0
            check=0
            requesteddata=datamodel()
            requesteddata.dataparams["datasource"]["requestquerystring"]=args
            requesteddata.dataparams["datasource"]["database"]["databasename"]=self.appdir +'\\login'
            requesteddata.dataparams["datasource"]["database"]["tablename"]=self.usertabledb
            #requesteddata.dataparams["datasource"]["websource"]["url"]='http://127.0.0.1:8000'
            #requesteddata.dataparams["datasource"]["websource"]["parameters"][0]["Tags"]='html18-22'
            #requesteddata.dataparams["datasource"]["websource"]["parameters"][0]["attributename"]='lang'
            #requesteddata.dataparams["datasource"]["websource"]["parameters"][0]["tagcontent"]='html18-22'
            #requesteddata.dataparams["datasource"]["websource"]["parameters"][0]["tagcontentoffset"]=100
            data1=requesteddata.retrievedata()
            argsstring="<div>"
            for keys in data1:
                argsstring+=str(data1[keys])
            argsstring+= "</div>"
            argslen=len(argsstring)
            updatecontent = str()
            idnum=1000
            try:
                for i in range(len(data1["Database"])):
                    updatecontent+= ("<form action='/delete.html' method='POST'><tr><td><input type=text name='id' value='" + parse.unquote((str(data1["Database"][i]["ROW_ID"])),encoding='UTF-8',errors="replace") + "'/></td><td><input type=email name='username' value='" + parse.unquote((str(data1["Database"][i]["username"])),encoding='UTF-8',errors="replace") + "'/></td><td><input name='password' id='"+str(idnum)+"' type=password onClick='unhidepass(this.id);' value='" + parse.unquote(str(self.DecryptCred(self.masterpass,data1["Database"][i]["password"]))[2:].strip("'"), encoding='utf-8', errors='replace') + "'/></td><td><input type=text name='applicationame' value='" + parse.unquote(str(data1["Database"][i]["applicationname"]), encoding='utf-8', errors='replace') + "'/></td><td><input type='url' value='" + parse.unquote(str(data1["Database"][i]["applicationurl"]), encoding='utf-8', errors='replace')+ "'/></td><td><input type='submit' id=123 name='Action' value='Delete account'></td></tr></form>")    
                    idnum+=1
            except KeyError as e:
                print("Database doesn't contain any passwords")
                pass
            except ValueError as e:
                print("Database Invalid value obtained from database!")
            updatecontent+="</table></body></html>"
            updateparams={"Tags": "td3008-3010" ,"attributename" : None, "attributevalue": None,"tagcontent": updatecontent, "tagcontentoffset":46 , "javascript": None, "javascriptoffset":None}
            prepareview=CustomViews(wfile,updateparams)
            prepareview.customview()
            self.send_response(code= 200,message='OK')
            self.send_header("ServerName","Server1")
            self.send_header("encoding","UTF-8")
            self.send_header("Pragma","No-Cache\r\n\n"+wfile["Updated"])   
            self.end_headers()
            dataargs={"filename": "login", "table":"users"} 

    def validatesession(self):
        dt=timedelta()
        try:
            for item in (self.headers.get_all("Cookie")):
                try:
                    if item.split("=")[0]=="session_id":
                        for user in self.authenticateduser:
                            if user==None:
                                continue
                            if(self.usersession[user]["session_id"]== item.split("=")[1]):
                                dt=datetime.today()-datetime.strptime(self.usersession[user]["last_login"],"%Y-%m-%d %H:%M:%S.%f")
                                if dt.total_seconds()<=900:
                                    self.usersession[user]["last_login"]= str(datetime.today())
                                    self.currentuser= user
                                    self.usertabledb=self.usersession[user]["dbname"]
                                    return True
                except ValueError as e:
                    print("Value Error:{}".format(e))
                except KeyError as e:
                    print("Invalid Session data({}) Error:{}".format(str(self.headers.get_all("Cookie")),e))
        except TypeError as e:
            print("Type Error:{}".format(e))
        return False

    def UserRegistration(self):
        createform=CustomViews(updateparams="")
        customhtml=createform.AddForm({"form":{"label":"User Registration", "action":"/userregistration.html", "method":"POST"},"fields":[{"label":"User Name", "name":"username", "type":"text", "value":"","placeholder":"Email Address"},{"label":"Password", "name":"password", "type":"password", "value":"","placeholder":"Password"}]})
        self.send_response(code= 200,message='OK')
        self.send_header("ServerName","Server1")
        self.send_header("encoding","UTF-8")
        self.send_header("Pragma","No-Cache\r\n\n"+customhtml["Updated"])   
        self.end_headers()

    def UserRegistrationPost(self,args):
        ID_Max=0
        db1 =database(filename= self.appdir+ "\\authenticate", table="users")
        db1.connect_database()
        for item in db1.retrieve_rows():
            if ID_Max < item['ROW_ID']:
                ID_Max = item['ROW_ID']
            if item["username"]==args["username"]:
                UserExists=1
                self.send_response(code= 301,message='Moved Temporarily')
                self.send_header("ServerName","Server1")
                self.send_header("encoding","UTF-8")
                self.send_header("location","http://127.0.0.1:8000/userregistration.html?action=page&number=1")   
                self.end_headers()
        #try:
        pwdhash=hashlib.new("SHA256")
        pwdhash.update(bytes(parse.unquote(args['password']),encoding="UTF-8"))
        db1.insert(dict(ROW_ID = ID_Max+1, username = parse.unquote(args['username']), password = str(pwdhash.digest()), masterenc=None))
        #except ValueError as e:
        #    print("Invalid value:{}".format(e))
        #except TypeError as e:
        #    print("Invalid value type:{}".format(e))
        #except KeyError as e:
        #    print("Invalid Key Name:{}".format(e))
        #except:
        #    print('database query Error')
        self.send_response(code= 301,message='Moved Temporarily')
        self.send_header("ServerName","Server1")
        self.send_header("encoding","UTF-8")
        self.send_header("location","http://127.0.0.1:8000/login.html?action=page&number=1")   
        self.end_headers()
        
    def authenticate(self, args):
            usertable=(parse.unquote(args['username'])).split('@')
            usertabledbint=str()
            for item1 in usertable:
                try:
                    usertabledbint+=item1.split('.')[0] + item1.split('.')[1]
                except IndexError as e:
                    print("Error:{}".format(e))
                    usertabledbint+=item1
            authdb=database(filename=self.appdir+ "\\authenticate",table="users")
            authdb.connect_database()
            query= 'select * from users where username=? and password=?'
            pwdhash=hashlib.new("SHA256")
            pwdhash.update(bytes(parse.unquote(args['password']),encoding="UTF-8"))
            userauth=authdb.userauthenticate((parse.unquote(args['username']), str(pwdhash.digest())))
            try:
                if(userauth['username']==parse.unquote(args['username'])):
                    if self.validateMaster(userauth['username']):
                        self.usersession[userauth['username']]={"session_id": str(secrets.token_hex(32)),"last_login": str(datetime.today()),"dbname": usertabledbint}
                        self.authenticateduser.append(userauth['username'])
                        return True
                    else:
                        return False
            except:
                print("Error occured in data from DB")
                
    def htmlresponse(self,statuscode,headers, statusmessage,response):
            self.send_response(code=statuscode, message= statusmessage)
            for item in headers.keys():
                self.send_header(item,headers[item])
            self.send_header("Pragma","No-Cache\r\n\n"+response)
            self.end_headers()
            
    def login_GET(self,args):
            wfile={"Default":"","Updated":""}
            cssfile=str()
            for line in fileinput.FileInput(self.appdir + "\\Application\\HTML\\login.html", mode='r'):
                wfile["Default"]+=line
            for line in fileinput.FileInput(self.appdir + "\\Application\\HTML\\main.css", mode='r'):
                cssfile+=line
            updateparams={"Tags": "html1-5" ,"attributename" : None, "attributevalue": None,"tagcontent": cssfile, "tagcontentoffset":47, "javascript": None, "javascriptoffset":None}
            prepareview=CustomViews(wfile,updateparams)
            prepareview.customview() 
            self.send_response(code= 200,message='OK')
            self.send_header("ServerName","Server1")
            self.send_header("Pragma","No-Cache\r\n\n"+prepareview.htmlpage["Updated"])
            self.end_headers()
            
    def validateMaster(self,username):
        self.masterpass=getpass.getpass(prompt="Master Password: ")
        masterauth=database(filename=self.appdir + "\\authenticate",table="users")
        masterauth.connect_database()
        queryres=masterauth.retrieve_rows()
        mastertext="This is a long string"
        for rows in queryres:
            if(rows["username"]==parse.unquote(username)):
                if(rows["masterenc"]!=None):
                    matchcount=0
                    while(matchcount<5):
                        if str(self.DecryptCred(self.masterpass,rows["masterenc"]))[2:].strip("'")==mastertext:
                            return True
                        else:
                            print("Master password entered was wrong...\n")
                            self.masterpass=getpass.getpass(prompt="Master Password: ")
                            matchcount+=1
                        return False
                else:
                    rows["masterenc"]=self.EncryptCred(self.masterpass, mastertext)
                    masterauth.update(rows["ROW_ID"],rows)
                    return True
            print("Username Not found!")
            
    def login_POST(self,args):
            wfile=dict()
            flogin=open(self.appdir+ "\\Application\\HTML\\login.html",mode="r")
            cssfile=open(self.appdir+ "\\Application\\HTML\\main.css",mode="r")
            updateparams={"Tags": "html1-5" ,"attributename" : None, "attributevalue": None,"tagcontent": cssfile.read(), "tagcontentoffset":12, "javascript": None, "javascriptoffset":None}
            wfile= {"Default": flogin.read(), "Updated": None}
            prepareview=CustomViews(wfile,updateparams)
            prepareview.customview()
            wfile["Default"]=prepareview.htmlpage['Updated']
            #wfile= {"Default": "<html><head></title>Password Management</title></head><body><div><form action='/login.html?action=page' method='POST'><fieldset><label for='username'>Username<label><input name='username' type='email' size='300px'></input><label for='password'>Password:<label><input name='password' type='password' size='300px'></input><input type='submit' name='Login' value='Login'/></fieldset></div></body></html>","Updated": None}
            authenticate=self.authenticate(args)
            if args==None or not(authenticate):
                response="<div color=#58FDAE align='center'>Username & password Not Found</div>"
                updateparams={"Tags": "div1154-1157" ,"attributename" : None, "attributevalue": None,"tagcontent": response, "tagcontentoffset":0 , "javascript": None, "javascriptoffset":None}
                loginerror=CustomViews(wfile,updateparams)
                loginerror.customview()
                wfile["Updated"]=loginerror.htmlpage['Updated']
                statuscode=401
                message="Unuthorized Request"
                headers={'Pragma': 'No-Cache'}
            elif(authenticate):
                statuscode=302
                headers={'location':'http://127.0.0.1:8000/index.html?action=page&number=1','Pragma': 'No-Cache',"Set-Cookie": ("session_id=") + str(self.usersession[parse.unquote(args["username"])]["session_id"])}
                message='Moved Temporarily'
            else:
                statuscode=401
                message='Unuthorized Request'
                headers={'Pragma': 'No-Cache'}
            if(wfile["Updated"]!=None):
                response=wfile["Updated"]
            else:
                response=wfile["Default"]
            if (statuscode==302 or statuscode==301):
                self.htmlresponse(statuscode,headers,message,"")
            else:
                self.htmlresponse(statuscode,headers,message,response)
                
    def logout(self):
            index=0
            user=str()
            for item in (self.headers.get_all("Cookie")):
                if(item.split("=")[0]=="session_id"):
                    usercookie= item.split("=")[1]
                    break
            for user in self.authenticateduser:
                if user==None:
                    continue
                elif self.usersession[user]["session_id"]==usercookie:
                    self.usersession[user]={"session_id": None,"last_login": None}
                    self.authenticateduser[index]=None
                    break
                index+=1
            statuscode=302
            headers={'location':'http://127.0.0.1:8000/login.html?action=page&number=1','Pragma': 'No-Cache'}
            message='Moved Temporarily'
            self.htmlresponse(statuscode,headers,message,"")
    
    def default(self):
            wfile = ""
            wfile = ("<html><head><link rel='shortcut icon' href='#' /></head><body><div><p>This is default response from server</p></div><div></div></body></html>")
            self.send_response(code= 302,message='Redirect')
            self.send_header("ServerName","Server1")
            self.send_header("Location","http://127.0.0.1:8000/login.html?action=page&number=1")
            self.send_header("Pragma","No-Cache\r\n\n"+wfile)
            self.end_headers()
    def printresponse(self,wfile):
            self.index({"page": "action", "number":1})
            self.send_response(code= 302,message='Moved Temporary')
            self.send_header("Server","Server1")
            self.send_header("location","http://127.0.0.1:8000/index.html?action=page&number=1")
            self.send_header("Pragma","No-Cache\r\n\n" + str(wfile))
            self.end_headers()
    def addaccount(self,args):
        ID_Max=0
        db1 =database(filename= self.appdir+ "\\login", table=self.usertabledb)
        db1.connect_database()
        for item in db1.retrieve_rows():
            if ID_Max < item['ROW_ID']:
                ID_Max = item['ROW_ID']
        try:
            db1.insert(dict(ROW_ID = ID_Max+1, username = args['User+Name'], password = self.EncryptCred(self.masterpass, args['Password']), applicationname = args['Application-Name'], applicationurl = args['Login-URL']))
            userdata= db1.retrieve_rows()
            wfile = ("<html><head><link rel='shortcut icon' href='#' /></head><body><div>")
            for i in range(0,len(userdata)):
                wfile+= ("<table><legend value='Add User'/><fieldset><tr><td>" + str(userdata[i]["username"]) + "</td><td>" + str(self.DecryptCred(self.masterpass,userdata[i]["password"]))[2:].strip("'") + "</td><td>" + str(userdata[i]["applicationname"]) + "</td><td>" + str(userdata[i]["applicationurl"]) + "</td></tr></fieldset>")
            statuscode=302
            headers={'location':'http://127.0.0.1:8000/index.html?action=page&number=1','Pragma': 'No-Cache'}
            message='Moved Temporarily'
            self.htmlresponse(statuscode,headers,message,"")
        except TypeError as e:
            print("Error occured while Enc/Dec{}: ".format(e))
            pass
        
    def deleteaccount(self,args):
        db1 =database(filename= self.appdir+ "\\login", table=self.usertabledb)
        db1.connect_database()
        db1.delete(args["id"])
        statuscode=302
        headers={'location':'http://127.0.0.1:8000/index.html?action=page&number=1','Pragma': 'No-Cache'}
        message='Moved Temporarily'
        self.htmlresponse(statuscode,headers,message,"")
        
    def applicationlogin(self,args):
        addhtml="<iframe src='" + args[applicationurl] +"'><iframe>"
        updateparams


    def EncryptCred(self, keydata,plaintextmsg):
        IV=(SHA256.new(bytes(keydata,encoding='UTF-8')).hexdigest())[:16]
        enckey = (SHA256.new(bytes(keydata,encoding='UTF-8')).hexdigest())[16:32]
        secobj= AES.new(bytes(enckey,encoding='UTF-8'), AES.MODE_CBC,bytes(IV,encoding='UTF-8'))
        encpassword=secobj.encrypt(pad(bytes(plaintextmsg,encoding='UTF-8'),16))
        return encpassword
        
    def DecryptCred(self, keydata, plaintextmsg):
        IV=(SHA256.new(bytes(keydata,encoding='UTF-8')).hexdigest())[:16]
        deckey = (SHA256.new(bytes(keydata,encoding='UTF-8')).hexdigest())[16:32]
        try:
            secobj= AES.new(bytes(deckey,encoding='UTF-8'), AES.MODE_CBC, bytes(IV,encoding='UTF-8'))
            decpassword=secobj.decrypt(plaintextmsg)
            return str(binascii.b2a_qp(unpad(decpassword,16)))
        except UnicodeDecodeError as e:
            print("Unicode Error:{}".format(e))
            return
        except ValueError as e:
            print("Value Error:{}".format(e))
            return
        except TypeError as e:
            print("Type Error:{}".format(e))
            return
        except KeyError as e:
            print("Key Error:{}".format(e))
            return

    def do_GET(self):
            args={}
            print("This is the Path" + self.path,"This is the page:" + self.path.split('?')[0].strip('/') + "Client_address:Client+Port" + str(self.client_address))
            try:
                for keyvalue in (self.path.split('?')[1].split('&')):
                    args[keyvalue.split('=')[0]]=(keyvalue.split('=')[1])
            except IndexError as e:
                print("Missing required parameters:{}".format(e))
            finally:
                if(self.path.split('?')[0].strip('/')=="index.html" and self.validatesession()):
                    self.index(args)
                elif(self.path.split('?')[0].strip('/')=="login.html"):
                    self.login_GET(args)
                elif(self.path.split('?')[0].strip('/')=="logout.html"):
                    self.logout()
                elif(self.path.split('?')[0].strip('/')=="userregistration.html"):
                    self.UserRegistration()
                elif(self.path.split('?')[0]=="/"):
                    self.default()
                else:
                    print("Invalid request")

    def do_POST(self):
        args={}
        argsquery=dict()
        decodedstr=(self.rfile.read1(4096)).decode(encoding='UTF-8', errors='strict')
        for i in range(len(decodedstr.split('&'))):
            args[decodedstr.split('&')[i].split("=")[0]] = decodedstr.split('&')[i].split("=")[1]
        print("This is the Path" + self.path,"This is the page:" + self.path.split('?')[0].strip('/'))
        try:
            for keyvalue in (self.path.split('?')[1].split('&')):
                argsquery[keyvalue.split('=')[0]]=(keyvalue.split('=')[1])
        except IndexError as e:
            print("Error:{}".format(e))
        finally:
            if(self.path.split('?')[0].strip('/')=="addaccount.html" and self.validatesession()):
                self.addaccount(args)
            elif(self.path.split('?')[0].strip('/')=="delete.html" and self.validatesession()):
                self.deleteaccount(args)
            elif(self.path.split('?')[0].strip('/')=="login.html"):
                self.login_POST(args)
            elif(self.path.split('?')[0].strip('/')=="userregistration.html"):
                self.UserRegistrationPost(args)
                    
def main():
    PORT=8000
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1",PORT),HTTPRequestClass)
    httpd.serve_forever()
    requesthandler=HTTPRequestClass()
    #requesthandler.do_GET()
    
if __name__=="__main__":main()
