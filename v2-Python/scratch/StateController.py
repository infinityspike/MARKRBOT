from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route("/")
def helloWorldTest() :
    return jsonify({'id':1,'msg':'Hello World'})

@app.route("/widget", methods=['GET'])
def getWidget() :
    id = request.args.get('id')
    print(id)
    pass

if __name__ == '__main__':
   app.run()