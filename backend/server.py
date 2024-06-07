from flask import Flask, request, jsonify
from compiler import compiler
from mongoengine import Document, StringField, EmailField, connect, ValidationError
from Authentication import Auth
from flask_cors import CORS
import pymongo
from Questions import Question


app = Flask(__name__)
CORS(app)

# In-memory storage for the example
data_store = {
    "message": "Hello, World! Nice to see you :)"
}

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CodeQuanta"]
user = mydb["user"]#collection for storing users
problems=mydb["problems"]#collection for storing problems



# Testing purpose
@app.route('/', methods=['GET'])
def get_data():
    return jsonify(data_store), 200

#registration
@app.route('/register',methods=['POST'])
def reg():
    data=request.json
    val=Auth.register(data,user)
    print(val)
    return jsonify(val['message']),val['code']

#login
@app.route('/login',methods=['POST'])
def login():
    data=request.headers.get('Authorization')
    value=''
    if(data is not None):
        data=data.split(' ')[1]
        value=Auth.login([data,1],user)
    else:
        data=request.json
        value=Auth.login([data,0],user)

    print(value)
    return jsonify(**value),value['code']

# Compile the code and get output
@app.route('/compile', methods=['POST'])
def compile():
    if not request.json :
        return jsonify({"error": "Invalid data"}), 400
    req = request.json
    if 'code' not in req or 'input' not in req or 'submission_id' not in req or 'extension' not in req or 'time_limit' not in req:
        res = {
            "message" : "Something is missing in request"
        }
        return jsonify(res), 400
    
    result = compiler.compile_and_run(req['code'],req['input'],req['submission_id'],req['extension'],req['time_limit'])
    res = {
        "status": result[0],
        "verdict": result[1]
    }
    return jsonify(res), 200


#add problems to the problems set
@app.route('/add-problems', methods=['POST'])
def addpb():
    data=request.json
    # print(data)
    # return jsonify(message='ok'),200
    value=Question.addquestions(data,problems)
    return jsonify(**value),value.get('code')


#GET all questions
#http://127.0.0.1:5000/questions?page=0
@app.route('/questions', methods=['GET'])
def getpb():
    page=0
    if(request.args.get('page')is not None):
        page=int(request.args.get('page'))
    qvalue=Question.getAllQuestions(problems,page)
    # print(jsonify(**qvalue))
    # return jsonify(message='ok'),200

    return jsonify(**qvalue),qvalue.get('code')

#get particular question
@app.route('/get-question', methods=['POST'])
def getparticularpb():
    data=request.json
    qvalue=Question.getParticularQuestion(problems,data.get('id'))
    # print(jsonify(**qvalue))
    # return jsonify(message='ok'),200

    return jsonify(**qvalue),qvalue.get('code')


if __name__ == '__main__':
    app.run(debug=True)
    # compiler.compile_and_run()


#Sample compile data
'''
{
    "code": "#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Hello, world!\" << endl;\n    int n;\n    cin >> n;\n\n    while(n--){\n        int x;\n        cin >> x;\n        cout << x*x <<\" \";\n    }\n    return 0;\n}\n"
,
    "input": "5\n1 2 3 4 5",
    "submission_id": "123",
    "extension": "cpp",
    "time_limit" : 2
}
'''