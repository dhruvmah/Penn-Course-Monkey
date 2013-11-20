from flask import Flask, g, jsonify, Response, request, json, render_template, redirect
from twilio.rest import TwilioRestClient
import redis
import os
import time
from penn.registrar import Registrar
app = Flask(__name__)


@app.before_request
def before_request():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    g.db = redis.from_url(redis_url)

@app.route('/thankyou')
def thankyou():
    g.db.srem("ACCT101001", "4158272831")
    return render_template("thankyou.html")

@app.route('/')
def splash():
    return render_template("splash.html")

@app.route('/form')
def form():
    return render_template("index.html")

@app.route('/removeclass', methods = ['POST'])
def removeNumberFromClass():
    number = cleansePhoneNumber(request.values.get('From', None))
    course = request.values.get('Body', None)
    g.db.srem(course, number)
    g.db.srem(number,course)
    print course
    print number
    return render_template("index.html")

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
@app.route('/account/<string:number>')
def show__classes(number):
    setCourses = g.db.smembers(number)
    return render_template("oneuser.html", s = setCourses)

@app.route('/addnumber', methods= ['POST'])
def add_number():
    add_info = request.form
    number = "1" + cleansePhoneNumber(add_info["number"])
    print number
    course = add_info["course"]
    print course
    g.db.sadd(course, number)
    g.db.sadd(number, course)
    return redirect('/account/'+ number)

@app.route('/pingserver')
def pingServer():
    print time.ctime()
    keys = g.db.keys()
    r = Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    for key in keys:
        if not (is_number(key)):
            course = r.search({'course_id': key})
            for x in course:
                print x["section_id"]
                print x["is_closed"]
                if (x["is_closed"] == False):
                    textUsers(x["section_id"])
    return redirect('/form')

@app.route('/getnumbers/<string:course_id>')
def listNumbersForClass(course_id):
    setNumbers = g.db.smembers(course_id)
    for x in setNumbers:
        print x
    return jsonify({"set": setNumbers})

def textUsers(course_id):
    setNumbers = g.db.smembers(course_id)
    for number in setNumbers:
        sendMessage(number, course_id)
    return

def sendMessage(number, course_id):
    account_sid = "AC42c5c65fb338266351c72a5c6e77d16c"
    auth_token  = "0f26d5e49d01724a708c5b30dce301f0"
    client = TwilioRestClient(account_sid, auth_token)    
    message = client.sms.messages.create(body=("Quick! There is 1 open seat in "+ course_id +"! Visit https://pennintouch.apps.upenn.edu/pennInTouch/jsp/fast2.do and register your course. Reply with" + course_id + " to stop receiving" + "messages. Peace out. "),
                 to="+"+ number,    # Replace with your phone number
                     from_="+18625792345") # Replace with your Twilio number
    print message.sid
    return jsonify({"status": message.sid})

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
    return render_template("courses.html", d = d)

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

if __name__ == '__main__':
    app.run(debug=True)
