Penn-Course-Monkey
==================

Penn Course Monkey is a webapp that allows users to sign up for text notifications, notifying them once a course opens up
for registration. 

app.py is the front-end server that handles a users actions on the website. It allows users to search for various classes
  and add their desired course. Once a user hits submit for a course, their phone number and course are stored in a redis
  database. 
  
The static and templates folders contain the html/css/images for the front-end.

worker.py is the back-end server that updates the redis database based on updates in the Penn Registrar Database. Since
  the database only allows 1,000 queries an hour, we query each class that has users signed up once per hour. Upon updating the data, we text users if their class is opened up. Worker.py runs on an Amazon EC2 instance. 
  
