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
class education:
    def __init__(self,eduid,public_id,school,degree,gpa,major,start_dtm,end_dtm,grad_dtm,grad_status,actv_prof,insrt_dtm,update_dtm):
        self.eduid=eduid
        self.public_id=public_id
        self.school=school
        self.degree=degree
        self.gpa=gpa
        self.major=major
        self.start_dtm=start_dtm
        self.end_dtm=end_dtm
        self.grad_dtm=grad_dtm
        self.grad_status=grad_status
        self.actv_prof=actv_prof
        self.insrt_dtm=insrt_dtm
        self.update_dtm=update_dtm
    def getjson(self):
        output={
        'eduid':self.eduid,
        'public_id':self.public_id,
        'school':self.school,
        'degree':self.degree,
        'gpa':self.gpa,
        'major':self.major,
        'start_dtm':self.start_dtm,
        'end_dtm':self.end_dtm,
        'grad_dtm':self.grad_dtm,
        'grad_status':self.grad_status,
        'actv_prof':self.actv_prof,
        'insrt_dtm':self.insrt_dtm,
        'update_dtm':self.update_dtm
        }

        return output

        
class myDatabase:
    def __init__(self):
        #self.con = sqlite3.connect('.myapi.db')
        self.con = sqlite3.connect('myapi.db')
        self.cur=self.con.cursor()
        self.create_table()
    def __del__(self):
        self.cur.close()
        self.con.close()
        print('Object Destroyed')
    def create_table(self):
        print(self.Check_user_table().data)
        print(self.Check_auth_table().data)
        print(self.Check_education_table().data)
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
            return Robject(False,str(e))
    #return object
    #Internal
    def Check_education_table(self):
        try:
            self.cur.execute('''CREATE TABLE education
                   (eduid INTEGER PRIMARY KEY AUTOINCREMENT,
                   public_id INTEGER NOT NULL,
                   school text NOT NULL,
                   degree text NOT NULL,
                   gpa text,
                   major text,
                   start_dtm text NOT NULL,
                   end_dtm text,
                   grad_dtm text,
                   grad_status text,
                   actv_prof text NOT NULL,
                   insrt_dtm text NOT NULL,
                   update_dtm text Not NULL)
                   ''')
            self.con.commit()
            print('education created')
            return Robject(True, 'User Table Created!')
        except Exception as e:
            return Robject(False,str(e))
    
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
    def addeducation_profile(self,public_id,school,degree,gpa,major,started_dtm,end_dtm,grad_dtm,grad_status):
        print(public_id,school,degree,gpa,major,started_dtm,end_dtm,grad_dtm,grad_status)

        datetime=str(dtm.datetime.now())
        try:
            self.cur.execute("INSERT INTO education VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            None,public_id,school,degree,gpa,major,started_dtm,end_dtm,grad_dtm,grad_status,'Y',datetime,datetime))
            self.con.commit()
            return Robject(True,'Education profile added!')
        except Exception as e:
            print(e)
            return Robject(False,str(e))
    def education_profile(self,public_id):
        self.cur.execute("SELECT * FROM education where public_id=?",(public_id,))
        result=self.cur.fetchall()
        print('------------------edcuation--------------')
        print(result)
        data=[]
        if len(result)==0:
            return Robject(False,'Education status not found!')
        else:
            for i in result:
                eduprofile=education(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12])
                data.append(eduprofile.getjson())
            return Robject(True,data)
                
