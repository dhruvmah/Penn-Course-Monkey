from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
from penn.registrar import Registrar
import pika
import time
import redis
import os
import app

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
db = redis.from_url(redis_url)

connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print ' [*] Waiting for messages. To exit press CTRL+C'

def is_number(s):
    try:
        float(s) 
        return True
    except ValueError: 
        return False
                
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    r = Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    keys = db.keys()
    for key in keys:
        if not (is_number(key)):
            if (key != ''):
                courses = r.search({'course_id': key}) 
                for course in courses:
                    db.hmset(course["section_id"], {'is_closed': course['is_closed']})
                    print course
                    print course["section_id"]
                    print course["is_closed"]
    print " [x] Done"
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                queue='task_queue')
channel.start_consuming()

