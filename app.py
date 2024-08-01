from flask import Flask,jsonify,request,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,create_refresh_token
import os 


app=Flask(__name__)
app.config.from_object('instance.config.Config')  

db=SQLAlchemy(app)
# using jwt validation 
jwt=JWTManager(app)


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
db.create_all()


# this method return all the records in our database 

@app.route('/')
def home():
    Students1= Students.query.all()
    return jsonify([{'id': item.id, 'name': item.username,"Passsword ":item.password} for item in Students1])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsoft.icon')


# this method is used only for fetcching one record at a time

@app.route('/get_student/<int:id>',methods=['GET'])
@jwt_required()
def get_one(id):
    data=Students.query.get(id)
    return jsonify({'id':data.id,'name':data.username,'password':data.password})


# this method is insert data in the database 
@app.route('/register',methods=['POST'])
def register():
    data=request.get_json()
    print(data)
    data=Students(username=data['username'],password=data['password'])
    db.session.add(data)
    db.session.commit()
    return jsonify({'message':"data added "+ data.username})

#this method is used for login 
@app.route('/login',methods=['POST'])
def login():
    json_data=request.get_json()
    data_database=Students.query.filter_by(username=json_data['username']).first()
    if data_database and data_database.password==json_data['password']:
        access_token=create_access_token(identity=data_database.id) # generate access token key by using flask_jwt_extended.create_access_token 
        refresh_token=create_refresh_token(identity=data_database.id) # generate refresh token key by using flask_jwt_extended.create_refresh_token
        return jsonify(access_token=access_token,refresh_token=refresh_token)
    return jsonify({"error":"Invalid credentials"}),401



# this method is used for updatig student data 

@app.route('/update-student/<int:id>',methods=['PUT'])
def update_student(id):
    table_ob=Students.query.get(id) #table_ob=table object 
    if table_ob:
        data=request.get_json()
        #table_ob.username=data['username']
        table_ob.password=data['password']
        db.session.commit()
        return jsonify({"response":"Data update sucessfully . "})
    else:
        return jsonify({"response":"Student ID does not exists. "})
    
    
    

#This method is used for delete user with the help of user id 

@app.route('/detele-student/<int:id>',methods=['DELETE'])
def delete_student(id):
    data=Students.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify({"response":"Student delete SucessFully .."})
    else:
        return jsonify({"response":"Userid does not exist ! "})
    

app.run(port=5001)