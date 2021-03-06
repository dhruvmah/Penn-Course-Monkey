#attempted to implement message queues here
from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
from twilio.rest import TwilioRestClient
import redis
import os
import time
from penn.registrar import Registrar
app = Flask(__name__)
import pika

@app.route('/pinger')
def pinger():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    message = "hi"
    channel.basic_publish(exchange='', 
                        routing_key="task_queue",
                        body = message,
                        properties = pika.BasicProperties(
                            delivery_mode = 1,
                        ))
    connection.close()
    return render_template("index.html")        

@app.before_request
def before_request():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    g.db = redis.from_url(redis_url)


@app.route('/thankyou')
def thankyou():
    return render_template("thankyou.html")

@app.route('/splash')
def splash():
    return render_template("splash.html")

@app.route('/')
def form():
    return render_template("index.html")

@app.route('/admin1737')
def adminDash():
    keys = g.db.keys()
    print keys
    dictKeys={}
    #for key in keys:
    #    if not (is_number(key)):
    #        dictKeys[key] = g.db.smembers(key)
    return render_template("admindashboard.html", d = dictKeys)

@app.route('/removeclass', methods = ['POST'])
def renewNumberForClass():
    number = cleansePhoneNumber(request.values.get('From', None))
    course = cleanseCourseID(request.values.get('Body', None))
    if (course != ""):
        g.db.sadd(course, number)
        g.db.sadd(number,course)
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
    course = cleanseCourseID(add_info["course"])
    print course
    if (number != ""):
        if (course != ""):
            g.db.sadd(course, number)
            g.db.sadd(number, course)
    return redirect('/account/'+ number)

@app.route('/pingserver')
def pingServer():
    print time.ctime()
#    keys = g.db.keys()
#    r = Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
#    for key in keys:
#        if not (is_number(key)):
#            if (key != "sent"):
#                if (key != ''):
#                    course = r.search({'course_id': key})
#                    for x in course:
#                        print time.ctime()
#                        print x["section_id"]
#                        print x["is_closed"]
#                        if (x["is_closed"] == False):
#                           textUsers(x["section_id"])
#   return redirect('/form')

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
        g.db.srem(number, course_id)
        g.db.srem(course_id, number)
    return

def sendMessage(number, course_id):
    account_sid = "AC42c5c65fb338266351c72a5c6e77d16c"
    auth_token  = "0f26d5e49d01724a708c5b30dce301f0"
    client = TwilioRestClient(account_sid, auth_token)    
    message = client.sms.messages.create(body=("Quick! " + course_id +" has 1 open seat. Register on PenninTouch. Reply with " + course_id + " to continue receiving messages. Love, Penn Course Monkey"),
                 to="+"+ number,    # Replace with your phone number
                     from_="+18625792345") # Replace with your Twilio number
    g.db.sadd("sent", (course_id + "number: " + number + " time: " + time.ctime()))
    return

@app.route('/course/', methods = ['POST'])
def listSectionStatus():
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
