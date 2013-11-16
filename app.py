from flask import Flask, g, jsonify, Response, request, json, render_template
import redis
import os
from penn.registrar import Registrar
app = Flask(__name__)


@app.before_request
def before_request():
    g.db= redis.StrictRedis(host="localhost", port = 6379)


@app.route('/')
def form():
    return render_template("form.html")


@app.route('/addnumber', methods= ['POST'])
def add_number():
    add_info = request.form
    number  = add_info["number"]
    print number
    course = add_info["course"]
    print course
    g.db.sadd(course, number)
    return jsonify({"status" : "okay",
            "number": number, "course": course})

@app.route('/getnumbers/<string:course_id>')
def listNumbersForClass(course_id):
    setNumbers = g.db.smembers(course_id)
    for x in setNumbers:
        print x
    return jsonify({"set": setNumbers})



@app.route('/course/<string:course_id>')
def listSectionStatus(course_id):
    r= Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    cis100s = r.search({'course_id': course_id})
    i=0
    d = {}
    for x in cis100s:
        print x["section_id"]
        s = x["section_id"]
        print s
        if x["is_closed"]:
            d[s] = "closed"
        else:
            d[s] = "open"
    return jsonify(d)

if __name__ == '__main__':
    app.run(debug=True)
