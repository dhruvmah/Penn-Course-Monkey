import redis
import os
from multiprocessing import Pool
from functools import partial
from twilio.rest import TwilioRestClient
import twilio
from penn.registrar import Registrar
import time

# setup database access
pool = redis.ConnectionPool(host='grideye.redistogo.com', port=9195, db=0, password="9affead30abd45aa2587a3bd66aee17e")
db = redis.Redis(connection_pool=pool)
r = Registrar("UPENN_OD_emoG_1000340", "7vgj93rojjmbuh3rrsgs7vc2ic")

# gets course info from course registrar, updates database, and texts users
def completeTask():
    #pool = Pool(5)
    #updated_courses = pool.map(get_opening, get_old_courses())
    updated_courses = [get_opening(course) for course in get_old_courses()]	
    #pool.map(update_database, updated_courses)
    for course in updated_courses:
        update_database(course)
    for course in updated_courses:
        text_open_courses(course)

#  gets courses from redis database
def get_old_courses():
    keys = db.keys()
    courses = []
    for key in keys:
        if not (is_number(key)) or (key == ''):
		try:
			course = db.hgetall(key)
        		course['id'] = key
        		courses.append(course)
		except redis.exceptions.ResponseError:
			print key + " " + "error"	
			db.delete(key)
    return courses

# used one time to populate the database with all courses
def load_all_courses():
    r = Registrar("UPENN_OD_emoG_1000340", "7vgj93rojjmbuh3rrsgs7vc2ic")
    courses = r.search({'course_id': ""})
        # runs once
    for c in courses:
        id = c['section_id']
	is_closed = (c['is_closed'] == True)
	try:
	    if (c["activity_description"] == "Lecture"):
	        instructor = c["instructors"][0]["name"]
            elif (c["activity_description"] == "Recitation"):
                instructor = c["primary_instructor"]
            else:
                instructor = ""
        except IndexError:
            instructor = ""
        print "adding: " + id
	db.hmset(id, {"id":id, "is_closed": is_closed, "instructor": instructor})

# checks registrar data to see if course is open
def get_opening(course):
    try:
    	print "get_opening"
    	r = Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    	courses = r.search({'course_id': course['id']})
    	# runs once
    	for c in courses:
		course['is_closed'] = (c['is_closed'] == True)
    		return course
    except OSError: 
    	print "error in get_opening"
    except ValueError as e:
	print e

# updates database with new course data
def update_database(course):
    if course is not None: 
    	try:
	    db.hset(course["id"], "is_closed", course['is_closed'])
    	    print course['is_closed']    
    	    if not course["is_closed"]:
    	        db.hset(course["id"], "numbers", "")
    	        keys = db.keys()
        except TypeError:
	    print course
	    print ("deleting" + course["id"])
	    db.delete(course["id"]) 

# figures out what numbers to text if a course is open
def text_open_courses(course):
	if course is not None:
		if not course["is_closed"]:
			if not course["numbers"] == "":
				numbers = course["numbers"].split(',')
				#pool = Pool(5)
				partial_course_send_message = partial(send_message, course_id=course['id'])
				#pool.map(partial_course_send_message, numbers)
				for number in numbers:
					partial_course_send_message(number) 

# sends text messages using Twilio API
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

# checks if a string is a number
def is_number(s):
    try:
        float(s) 
        return True
    except ValueError: 
        return False

if __name__ == '__main__':
	while True:
		print "start tast"
		completeTask()
		print "sleep"
		time.sleep(3600)
