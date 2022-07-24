from flask import Flask,request,jsonify,make_response
import time
import datetime
from functools import wraps
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dbmanagement import *


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
            except:
                return jsonify({'message':'Token is invalid! please Login and get token.'}),401
        else:
            return jsonify({"message":"Please provide token!"})
    return wrapper

@app.route('/',methods=['GET','POST'])
@tokendecoder
def Home(userid):
    currenttime=time.ctime()
    return jsonify({"message": "Welcome to Home page "+userid+" " + currenttime})


@app.route('/users',methods=['POST'])
@tokendecoder
def users(userid):
    DB=myDatabase()
    result=DB.display_users()
    del DB
    return jsonify({"message": result})

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
        if result[0]==True:
            user=result[1]
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
            if res==True:
                return jsonify({"message":"user created"})
            else:
                return jsonify({"message":str(res)})
                
    except Exception as e:
        print(e)
        return jsonify({"message":'Please send appropriate json format as provided'})

if __name__=='__main__':
    app.run(debug=True)
