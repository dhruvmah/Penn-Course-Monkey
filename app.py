from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
from twilio.rest import TwilioRestClient
import redis
import os
import time
from penn.registrar import Registrar
app = Flask(__name__)
       
@app.before_request
def before_request():
    pool = redis.ConnectionPool(host='grideye.redistogo.com', port=9195, db=0, password="9affead30abd45aa2587a3bd66aee17e")
    g.db = redis.Redis(connection_pool=pool)

@app.route('/thankyou')
def thankyou():
    return render_template("thankyou.html")

@app.route('/splash')
def splash():
    return render_template("splash.html")

@app.route('/')
def form():
    return render_template("index.html")

# deprecated keys
@app.route('/admin1737')
def adminDash():
    keys = g.db.keys()
    print keys
    dictKeys={}
    #for key in keys:
    #    if not (is_number(key)):
    #        dictKeys[key] = g.db.smembers(key)
    return render_template("admindashboard.html", d = dictKeys)

# allows user to text in and re-sign up for a course
@app.route('/renewclass', methods = ['POST'])
def renewNumberForClass():
    number = cleansePhoneNumber(request.values.get('From', None))
    course = cleanseCourseID(request.values.get('Body', None))
    if not (course == "" or number == ""):
        submit_course_into_db(number, course);
    return render_template("index.html")

# cleanse number prior to registering user
@app.route('/addnumber', methods= ['POST'])
def add_number():
    add_info = request.form
    number = "1" + cleansePhoneNumber(add_info["number"])
    course = cleanseCourseID(add_info["course"])
    submit_course_into_db(number, course) 
    return redirect('/account/'+ number)

# registers the user to receive notifications 
def submit_course_into_db(number, course):
    if not (course == "" or number == ""):
        number_string = g.db.hget(course, "numbers")
        if number_string is None:
            number_string = number
        else:
            number_string = number_string + "," + number
        g.db.hset(course, "numbers", number_string)
        g.db.sadd(number,course)

# checks if a string is a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
# shows a user which courses he/she has signed up for
@app.route('/account/<string:number>')
def show__classes(number):
    setCourses = g.db.smembers(number)
    return render_template("oneuser.html", s = setCourses)

@app.route('/clearCourse/<string:course>')
def clear_course(course):
    g.db.hset(course, "numbers", "")
    keys = g.db.keys()
    for key in keys:
        if is_number(key):
            g.db.srem(key, course)
    return render_template("index.html")

# looks up course for the user
@app.route('/course/', methods = ['POST'])
def listSectionStatus():
    try:
        requested = request.form
        r= Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
        course = r.search({'course_id': requested['course_id']})
        d = {}
        for x in course:
            l = []
            s = x["section_id"]
            print ("section" + s)
            if x["is_closed"]:
                l.append("Closed")
                print "is_closed"
            else:
                l.append("Open")
                print "is _open"
            if (x["activity_description"] == "Lecture"):
                p = x["instructors"][0]["name"]
            elif (x["activity_description"] == "Recitation"):
                p = x["primary_instructor"]
            else:
                p = ""
            print "professor: " + p
            l.append(p)
            t = x["first_meeting_days"]
            print "time: " + t
            l.append(t)
            d[s] = l
        return render_template("courses.html", d = d)
    except ValueError as e:
        return render_template("courses.html", d={})

def cleansePhoneNumber(number):
	#I assumed number was a string
	#I used the string replace() method
	#http://www.tutorialspoint.com/python/string_replace.htm
    number=number.replace('(','')
    number=number.replace(' ','')
    number=number.replace(')','')
    number=number.replace('.','')
    number=number.replace('+','')
    number=number.replace('-','')
    number=number.replace('[','')
    number=number.replace(']','')
    return number

def cleanseCourseID(number):
    #I assumed number was a string
    #I used the string replace() method
    #http://www.tutorialspoint.com/python/string_replace.htm
    number=number.replace('(','')
    number=number.replace(' ','')
    number=number.replace(')','')
    number=number.replace('.','')
    number=number.replace('+','')
    number=number.replace('-','')
    number=number.replace('[','')
    number=number.replace(']','')
    number=number.upper()
    return number

if __name__ == '__main__':
    app.run(debug=True)
