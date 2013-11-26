import redis
import os
from multiprocessing import Pool
from functools import partial
from twilio.rest import TwilioRestClient
import twilio
from penn.registrar import Registrar
import time

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
db = redis.from_url(redis_url)
r = Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")

def completeTask():
    #pool = Pool(5)
    #updated_courses = pool.map(get_opening, get_old_courses())
    updated_courses = [get_opening(course) for course in get_old_courses()]	
    #pool.map(update_database, updated_courses)
    for course in updated_courses:
    	update_database(course)
    for course in updated_courses:
        text_open_courses(course)

def get_old_courses():
    keys = db.keys()
    courses = []
    for key in keys:
        if not (is_number(key)) and (key != ''):
        	course = db.hgetall(key)
        	course['id'] = key
        	courses.append(course)
    return courses

def get_opening(course):
    try:
    	print "get_opening"
    	r = Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    	courses = r.search({'course_id': course['id']})
    	# runs once
    	for c in courses:
    		course['is_closed'] = (c['is_closed'] == 'True')
    		return course
    except OSError: 
    	print "error in get_opening"
    	return 

def update_database(course):
    db.hset(course["id"], "is_closed", course['is_closed'])
    if not course["is_closed"]:
    	db.hset(course["id"], "numbers", "")
    	keys = db.keys()
    	for key in keys:
            if is_number(key):
                print "phone number:" + key
                db.srem(key, course["id"])

def text_open_courses(course):
	if not course["is_closed"]:
		if not course["numbers"] == "":
			numbers = course["numbers"].split(',')
			#pool = Pool(5)
			partial_course_send_message = partial(send_message, course_id=course['id'])
			#pool.map(partial_course_send_message, numbers)
			for number in numbers:
				partial_course_send_message(number) 

def send_message(number, course_id):
	try:
		account_sid = "AC42c5c65fb338266351c72a5c6e77d16c"
		auth_token  = "0f26d5e49d01724a708c5b30dce301f0"
		client = TwilioRestClient(account_sid, auth_token)
		message = client.sms.messages.create(body=("Quick! " + course_id +" has 1 open seat. Register on PenninTouch. Reply with " + course_id + " to continue receiving messages. Love, Penn Course Monkey"),
        	         to="+1"+ number,    # Replace with your phone number
           	          from_="+18625792345") # Replace with your Twilio number
		db.sadd("1737", (course_id + "number: " + number + " time: " + time.ctime()))
		print number
	except twilio.TwilioRestException as e:
		print e

def is_number(s):
    try:
        float(s) 
        return True
    except ValueError: 
        return False

if __name__ == '__main__':
	while True:
		print "sleeping"
		time.sleep(200)
		print "start tast"
		completeTask()
