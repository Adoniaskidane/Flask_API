from unittest import result
from flask import Flask,request,jsonify,make_response, url_for, render_template
import time
import datetime
from functools import wraps
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dbmanagement import *
#from .dbmanagement import *


app=Flask(__name__)

app.config['SECRET_KEY']='You are the key'
rootDomain='https://www.akmnow.com/'
rootDomain='http://127.0.0.1:5000/'

#*****************Main page*********************************
DomainName=[rootDomain,rootDomain+'auth',rootDomain+'feature',rootDomain+'service',rootDomain+'docs',rootDomain+'resume']
@app.route('/')
@app.route('/home')
def index():
   return render_template("index.html",domain=DomainName)

@app.route('/auth',methods=['GET','POST'])
def Authenticate():
    if request.method=="GET":
        return render_template("auth.html",domain=DomainName,token='Token will be here when Autorized!')
    elif request.method=="POST":
        newauth=Auth()
        newresult=newauth.UI_Login(request.form['username'],request.form['password'])
        print(newresult)
        if newresult[0] == True:
            return render_template("auth.html",domain=DomainName,token=newresult[1])
        else:
            return render_template("auth.html",domain=DomainName,token=newresult[1])
    elif request.method=="PUT":
        pass
        print('puttttttttt')
        return render_template("auth.html",domain=DomainName,token='Signing up!')
        
@app.route('/feature')
def feature():
    return render_template("feature.html",domain=DomainName)

@app.route('/service')
def Services():
    return render_template("service.html",domain=DomainName)
    
@app.route('/docs')
def docs():
    return render_template("docs.html",domain=DomainName)

@app.route('/resume')
def resume():
    return render_template("resume.html",domain=DomainName)

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

@app.route('/api',methods=['GET','POST'])
#@tokendecoder
def Home():#userid):
    currenttime=time.ctime()
    userid='user'
    return jsonify({"message": "Welcome to Home page "+userid+" " + currenttime})

@app.route('/api/user/<public_id>',methods=['GET','POST'])
@tokendecoder
def user(userid,public_id):
    DB=myDatabase()
    res=DB.get_user(public_id)
    del DB
    try:
        return jsonify({"message": res})
    except:
        return jsonify({"message": res})

@app.route('/api/users',methods=['POST'])
@tokendecoder
def users(userid):
    DB=myDatabase()
    result=DB.display_users()
    del DB
    return jsonify({"message": result})

@app.route('/api/update_username/<username>',methods=['POST'])
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


        
@app.route('/api/promote_user/<public_id>',methods=['POST'])
@tokendecoder
def promote_user(userid,public_id):
    DB=myDatabase()
    res=DB.promote_user(userid,public_id)
    DB.display_users()
    return jsonify({'message':res.data})

#adding education profile
@app.route('/api/addeducation_profile',methods=['POST'])
@tokendecoder
def addeducation_profile(public_id):
    data=request.get_json()
    try:
        school=data['school']
        degree=data['degree']
        gpa=data['gpa']
        major=data['major']
        started_dtm=data['started_dtm']
        end_dtm=data['end_dtm']
        grad_dtm=data['grad_dtm']
        grad_status=data['grad_status']
        
        if school.strip(' ') and degree.strip(' ') and gpa.strip(' ') and major.strip(' ') and started_dtm.strip(' ') and end_dtm.strip(' ') and grad_dtm.strip(' ') and grad_status.strip(' '):
            DB=myDatabase()
            res=DB.addeducation_profile(public_id,school,degree,gpa,major,started_dtm,end_dtm,grad_dtm,grad_status)
            DB.display_users()
            del DB
            return jsonify({'message':res.data})
        else:
            return jsonify({'message':'please provide a valid json format!'})
    except Exception as e:
        print(e)
        return jsonify({"message":'Please send appropriate json format as provided'})

@app.route('/api/education_profile',methods=['GET'])
@tokendecoder
def education_profile(public_id):
    try:
        DB=myDatabase()
        res=DB.education_profile(public_id)
        del DB
        return jsonify({'message':res.data})
    except Exception as e:
        return jsonify({'message':str(e)}),401

@app.route('/api/login', methods=['GET','POST'])
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

@app.route('/api/signup', methods=['POST'])
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


class Auth:
    def __init__(self) -> None:
         pass

    def UI_Login(self,username, password):
        if username!="" and password!="":
                print("UI Auth Username: ", username ,"Password: ",password)
                data=[{"username":username},{"password":password}]
                DB=myDatabase()
                result=DB.authenticate(username,password)
                if result.value==True:
                    user=result.data
                    currenttime=datetime.datetime.utcnow()
                    expires=currenttime+datetime.timedelta(minutes=30)
                    token=token=jwt.encode({'public_id':user.public_id,'exp':expires},app.config['SECRET_KEY'],algorithm="HS256")
                    DB.add_authrized_user(user,token,currenttime,app.config['SECRET_KEY'])
                    
                    return [True, token]
                else:
                    return [False, "Invalid Username or Password!"]
        else:
            return [False, "Invalid Username or Password!"]



if __name__=='__main__':
    app.run(debug=True)
