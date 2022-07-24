import sqlite3
import hashlib
import time


class user:
    def __init__(self,Id,public_id,firstname,lastname,email,username,password,admin,datetime):
        self.id=Id
        self.public_id=public_id
        self.firstname=firstname
        self.lastname=lastname
        self.email=email
        self.username=username
        self.password=password
        self.admin=admin
        self.datetime=datetime

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
               'datetime': self.datetime
            }
        return output
        
class myDatabase:
    def __init__(self):
        self.con = sqlite3.connect('myapi.db')
        self.cur=self.con.cursor()
        self.create_table()
        print("------------------------------------")
        print('* DB connection build and ready.')
        print('* Table created or existed')
        print("------------------------------------")
    def __del__(self):
        self.cur.close()
        self.con.close()
        print('Object Destroyed')
    def create_table(self):
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
               datetime text NOT NULL)
               ''')
            self.con.commit()
            print('users created')
        except Exception as e:
            print(e)
        finally:
            try:
                self.cur.execute('''CREATE TABLE auth
                   (authid INTEGER PRIMARY KEY AUTOINCREMENT,
                   id INTEGER NOT NULL,
                   public_id INTEGER NOT NULL,
                   token text NOT NULL UNIQUE,
                   key text NOT NULL,
                   datetime text NOT NULL)
                   ''')
                self.con.commit()
                print('auth created')
            except Exception as e:
                print(e)

    def insert_user(self,first,last,email,user,passw):
        datetime=time.ctime()
        hashpass= hashlib.md5((str(passw)).encode()).hexdigest()
        data=first+last+email+user+hashpass+datetime
        result = hashlib.md5(data.encode()).hexdigest()
        try:
            self.cur.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
            (None,result,first,last,email,user,passw,0,datetime))
            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return e

    def display_users(self):
        self.cur.execute("SELECT * FROM users")
        result=self.cur.fetchall()
        data=[]
        for i in result:
            print(i)
            output={
                'id':i[0],
               'public_id':i[1],
               'firstname':i[2], 
               'lastname':i[3],
               'email':i[4],
               'username':i[5],
               'password':i[6],
               'admin':i[7],
               'datetime':i[8]
            }
            data.append(output)
        return data

    def authenticate(self,username,password):
        query="SELECT * FROM users WHERE username='"+username+"' and password='"+password+"'"
        self.cur.execute(query)
        result=self.cur.fetchall()
        if len(result)==0:
            return [False,result]
        else:
            data=result[0]
            self.user=user(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
            return [True,self.user]


    def add_authrized_user(self,user,token,datetime,key):
        try:
            self.cur.execute("INSERT INTO auth VALUES (?,?,?,?,?,?)",
            (None,user.id,user.public_id,token,key,datetime))
            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return e

        
        
