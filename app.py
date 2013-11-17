from flask import Flask, g, jsonify, Response, request, json, render_template, redirect
import redis
import os
from penn.registrar import Registrar
app = Flask(__name__)


@app.before_request
def before_request():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    g.db = redis.from_url(redis_url)

@app.route('/')
def form():
    return render_template("index.html")

@app.route('/account/<string:number>')
def show__classes(number):
    setCourses = g.db.smembers(number)
    return render_template("classes.html", s = setCourses)

@app.route('/addnumber', methods= ['POST'])
def add_number():
    add_info = request.form
    number  = add_info["number"]
    print number
    course = add_info["course"]
    print course
    g.db.sadd(course, number)
    g.db.sadd(number, course)
    return redirect('/account/'+ number)

@app.route('/getnumbers/<string:course_id>')
def listNumbersForClass(course_id):
    setNumbers = g.db.smembers(course_id)
    for x in setNumbers:
        print x
    return jsonify({"set": setNumbers})

@app.route('/course/', methods = ['POST'])
def listSectionStatus():
    requested = request.form
    r= Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    course = r.search({'course_id': requested['course_id']})
    d = {}
    for x in course:
        print x["section_id"]
        s = x["section_id"]
        print s
        if x["is_closed"]:
            d[s] = "closed"
        else:
            d[s] = "open"
    return render_template("form.html", d = d)

if __name__ == '__main__':
    app.run(debug=True)
