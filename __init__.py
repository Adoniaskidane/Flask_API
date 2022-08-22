from flask import Flask,request,jsonify,make_response
import time
import datetime
from functools import wraps
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dbmanagement import *
import sqlite3
import hashlib
import datetime as dtm

#this is return object which all of the function has to return
#value rep True/False
#data rep if there is a data,Error,string or anyinfo need to be passed

class Robject:
    def __init__(self,value,data):
        self.value=value
        self.data=data
class customuser:
    def __init__(self,Id,public_id,firstname,lastname,email,username,password,admin,actv_usr,insrt_dtm,joined_dtm):
        self.id=Id
        self.public_id=public_id
        self.firstname=firstname
        self.lastname=lastname
        self.email=email
        self.username=username
        self.password=password
        self.admin=admin
        self.actv_usr=actv_usr
        self.insrt_dtm=insrt_dtm
        self.joined_dtm=joined_dtm

    def getjson(self):
        output={
                'id':self.id,
               'public_id':self.public_id,
               'firstname':self.firstname, 
               'lastname': self.lastname,
               'email':self.email,
               'username': self.username,
               'password':self.password,
               'admin':self.admin,
                'actv_usr':self.actv_usr,
               'insrt_dtm':self.insrt_dtm,
                'joined_dtm':self.joined_dtm
            }
        return output
        
class myDatabase:
    def __init__(self):
        self.con = sqlite3.connect('myapi.db')
        self.cur=self.con.cursor()
        self.create_table()
    def __del__(self):
        self.cur.close()
        self.con.close()
        print('Object Destroyed')
    def create_table(self):
        self.Check_user_table
        self.Check_auth_table()
    #return object
    #Internal
    def Check_user_table(self):
        try:
            self.cur.execute('''CREATE TABLE users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            public_id INTEGER NOT NULL UNIQUE,
            firstname text NOT NULL, 
            lastname text NOT NULL,
            email text NOT NULL UNIQUE,
            username text NOT NULL UNIQUE,
            password text NOT NULL,
            admin INTEGER DEFAULT 0,
            actv_usr text NOT NULL,
            insrt_dtm text NOT NULL,
            joined_dtm text NOT NULL)
            ''')
            self.con.commit()
            print('users created')
            return Robject(True,'User Table Created!')
        except Exception as e:
            print(e)
            return Robject(False,str(e))
    #return object
    #Internal
    def Check_auth_table(self):
        try:
            self.cur.execute('''CREATE TABLE auth
                   (authid INTEGER PRIMARY KEY AUTOINCREMENT,
                   id INTEGER NOT NULL,
                   public_id INTEGER NOT NULL,
                   token text NOT NULL UNIQUE,
                   key text NOT NULL,
                   insrt_dtm text NOT NULL)
                   ''')
            self.con.commit()
            print('auth created')
            return Robject(True, 'User Table Created!')
        except Exception as e:
            print(e)
            return Robject(False,str(e))
    def Check_edu_profile_table(self):
        pass
    #adding a new user to users table
    #return object
    def insert_user(self,first,last,email,user,passw):
        datetime=str(dtm.datetime.now())
        hashpass= hashlib.md5((str(passw)).encode()).hexdigest()
        data=first+last+email+user+hashpass+datetime
        result = hashlib.md5(data.encode()).hexdigest()
        try:
            self.cur.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (None,result,first,last,email,user,passw,0,'Y',datetime,datetime))
            self.con.commit()
            return Robject(True,'Hi '+ user+' You account is created, login and get token!')
        except Exception as e:
            print(e)
            return Robject(False,str(e))

    #fun to return all users
    def display_users(self):
        self.cur.execute("SELECT * FROM users")
        result=self.cur.fetchall()
        data=[]
        for i in result:
            curuser=customuser(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10])            
            finaljson=curuser.getjson()
            data.append(finaljson)
        return data

    #authentication: to autorize and deny with username and password
    #return object
    def authenticate(self,username,password):
        query="SELECT * FROM users WHERE username='"+username+"' and password='"+password+"'"
        self.cur.execute(query)
        result=self.cur.fetchall()
        if len(result)==0:
            return Robject(False,result)
        else:
            data=result[0]
            self.user=customuser(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10])
            return Robject(True,self.user)

    #when user autorized add to Auth DB(data collection)
    #return object
    def add_authrized_user(self,user,token,datetime,key):
        try:
            self.cur.execute("INSERT INTO auth VALUES (?,?,?,?,?,?)",
            (None,user.id,user.public_id,token,key,datetime))
            self.con.commit()
            return Robject(True,'auth log added!')
        except Exception as e:
            print(e)
            return Robject(False,str(e))

    #return object
    def get_user(self,public_id):
        self.cur.execute("SELECT * FROM users where public_id=?",(public_id,))
        result=self.cur.fetchall()
        data=[]
        if len(result)==0:
            return Robject(False,'Invalid User ID!')
        elif len(result)!=1:
            return Robject(False,'cound not find the user, please report to us! Internal Issue!!')
        else:
            for i in result:
                newuser=customuser(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10])
                finaljson=newuser.getjson()
                data.append(finaljson)
            return Robject(True,data)

    #promote user to admin, the current user must be admin to promote
    #return object
    def promote_user(self,userid,public_id):
        try:
            self.cur.execute("UPDATE users SET admin=1 where public_id=?",(public_id,))
            self.con.commit()
            data= 'Congradulation, User '+public_id+' has been promoted!'
            return Robject(True,data)
        
        except Exception as e:
            return Robject(True,str(e))


app=Flask(__name__)

app.config['SECRET_KEY']='You are the key'

def tokendecoder(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        token=None
        if 'token' in request.headers:
            token=request.headers['token']
            try:
                data=jwt.decode(token,app.config['SECRET_KEY'], algorithms=["HS256"])
                print(data)
                result=f(data['public_id'],*args,**kwargs)
                return result
            except Exception as e:
                print(e)
                return jsonify({'message':'Token is invalid! please Login and get token. Reason: ' +str(e)}),401
        else:
            return jsonify({"message":"Please provide token!"})
    return wrapper

@app.route('/',methods=['GET','POST'])
@tokendecoder
def Home(userid):
    currenttime=time.ctime()
    return jsonify({"message": "Welcome to Home page "+userid+" " + currenttime})

@app.route('/user/<public_id>',methods=['GET','POST'])
@tokendecoder
def user(userid,public_id):
    DB=myDatabase()
    res=DB.get_user(public_id)
    del DB
    try:
        return jsonify({"message": res})
    except:
        return jsonify({"message": res})

@app.route('/users',methods=['POST'])
@tokendecoder
def users(userid):
    DB=myDatabase()
    result=DB.display_users()
    del DB
    return jsonify({"message": result})

@app.route('/update_username/<username>',methods=['POST'])
@tokendecoder
def update_username(userid,username):
    data=request.get_json()
    try:
        firstname=data['firstname']
        lastname=data['lastname']
        email=data['email']
        username=data['username']
        password=data['password']
        if data['username']!='' and data['password']!='' and data['firstname']!='' and data['lastname']!='' and data['email']!='':
            DB=myDatabase()
            #update user here
            DB.display_users()
            del DB
            return jsonify({'message':'updating in process...'})
    except:
        return jsonify({'message':'updating is not in process...'})


        
@app.route('/promote_user/<public_id>',methods=['POST'])
@tokendecoder
def promote_user(userid,public_id):
    DB=myDatabase()
    res=DB.promote_user(userid,public_id)
    DB.display_users()
    return jsonify({'message':res.data})

#adding education profile
@app.route('/add_education_profile',methods=['POST'])
@tokendecoder
def add_education_profile(public_id):
    data=request.get_json()
    print(data)
    for i in data:
        print(i)
    return data    

@app.route('/login', methods=['GET','POST'])
def login():
    auth=request.authorization
    if auth and auth.password and auth.username:
        print(auth)
        print(auth.username)
        print(auth.password)
        data=[{"username":auth.username},{"password":auth.password}]
        DB=myDatabase()
        result=DB.authenticate(auth.username,auth.password)
        if result.value==True:
            user=result.data
            currenttime=datetime.datetime.utcnow()
            expires=currenttime+datetime.timedelta(minutes=30)
            token=token=jwt.encode({'public_id':user.public_id,'exp':expires},app.config['SECRET_KEY'],algorithm="HS256")
            DB.add_authrized_user(user,token,currenttime,app.config['SECRET_KEY'])
            
            return jsonify({"token":token})
    return make_response('Could not Verify',401,{'WWW-Authenticate': 'Basic realm="Login required!"' })

@app.route('/signup', methods=['POST'])
def signup():
    data=request.get_json()
    try:
        firstname=data['firstname']
        lastname=data['lastname']
        email=data['email']
        username=data['username']
        password=data['password']
        
        if data['username']!='' and data['password']!='' and data['firstname']!='' and data['lastname']!='' and data['email']!='':
            DB=myDatabase()
            res=DB.insert_user(firstname,lastname,email,username,password)
            DB.display_users()
            del DB
            if res.value==True:
                return jsonify({"message":res.data})
            else:
                return jsonify({"message":res.data})
        else:
            return jsonify({'message': "provide full json please!"})
                
    except Exception as e:
        print(e)
        return jsonify({"message":'Please send appropriate json format as provided'})


if __name__=='__main__':
    app.run(debug=True)
