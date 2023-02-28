######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from datetime import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'VHwan145694'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()	#connecting to mysql
cursor = conn.cursor()	#creating cursor object using cursor() method, to make connection for executing queries 
cursor.execute("SELECT email from Users")	#executes an SQL query
users = cursor.fetchall()	 #fetches all rows of a querey result, returning a list

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register/", methods=['POST'])
def register_user():
	try:	#test block of code for errors
		email=request.form.get('email')
		password=request.form.get('password')
		firstname=request.form.get('firstname')
		lastname=request.form.get('lastname')
		gender=request.form.get('gender')
		dob=request.form.get('dob')
		hometown=request.form.get('hometown')
		score = 0

	except:	#for handling the error
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, firstname, lastname, gender, dob, hometown, score)\
		       VALUES ('{0}', '{1}', '{2}', '{3}','{4}', '{5}', '{6}', '{7}')"\
		       .format(email, password, firstname, lastname, gender, dob, hometown, score)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

# begin friendships code 

# for finding friend by email
@app.route('/friends', methods=['GET','POST']) # GET = retrieving element, POST = adding element
@flask_login.login_required
def addfriends():
		if request.method == 'POST':
			try:
				friend_email = request.form.get('friend_email')
			except:
				print("couldn't find all token") #this prints to shell, end users will not see this (all print statements go to shell)
				return render_template('riends.html')
			
			user_email = flask_login.current_user.id

			if user_email == friend_email:
				return render_template('friends.html', message='You cannot be friends with yourself!')
			elif alreadyFriends(user_email, friend_email):
				return render_template('friends.html', message='You are already friends with this person!')
			else:
				user_id = getUserIdFromEmail(flask_login.current_user.id)
				friend_id = getUserIdFromEmail(friend_email)
				cursor = conn.cursor()

				print(cursor.execute("INSERT INTO photoshare.FriendsWith (user_id, friend_id) VALUES ('{0}', '{1}')".format(user_id, friend_id)))
				conn.commit()
				return render_template('friends.html', message='Friend Added!')

		else:
			return render_template('friends.html')
	
	


# helper methods for friends():
# given a user's email, returns 3 emails of friends of friends who are not already friends with the user

def getRecFriends(user_email):
	recs = []
	user_friends = getFriends(user_email)

	count = 0
	for friend in user_friends: # friends of friends implementation
		friends_of_friend = getFriends(friend)
		for person in friends_of_friend:
			if (not alreadyFriends(user_email, person)) and (person not in recs) and (count < 3) and (not user_email == person):
				recs.append(person)
				count += 1

	if count < 5: 
		cursor = conn.cursor()
		cursor.execute("SELECT email FROM Users WHERE email <> '{0}'".format(user_email)) # all users who aren't the current user
		people = cursor.fetchall() # list of tuples, [(email1), (email2), ...]

		for person in people:
			if (not alreadyFriends(user_email, person[0])) and (person[0] not in recs) and (count < 3) and (not person[0] == 'anon@anon.com'):
				recs.append(person[0])
				count += 1

	return recs

def searchFriend(email):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname, email FROM Users WHERE email = '{0'".format(email))
	return cursor.fetchall()

def alreadyFriends(user_email, friend_email):
	# returns true if the user is not already friends with that person
	user_id = getUserIdFromEmail(user_email)
	friend_id = getUserIdFromEmail(friend_email)
	cursor = conn.cursor()

	if cursor.execute("SELECT * FROM FriendsWith WHERE user_id = '{0}' AND friend_id = '{1}'".format(user_id, friend_id)):
		return True
	elif cursor.execute("SELECT * FROM FriendsWith WHERE user_id = '{1}' AND friend_id = '{0}'".format(user_id, friend_id)):
		return True
	else: 
		return False
	
	# given user email, returns that user's user ID
# given user ID, returns that user's email
def getEmailFromUserId(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()[0]

# given a user's email, returns a list of their friends' emails
def getFriends(user_email):
	uid = getUserIdFromEmail(user_email)
	cursor = conn.cursor()

	cursor.execute("SELECT friend_id FROM FriendsWith WHERE user_id = '{0}'".format(uid))
	friends = cursor.fetchall() # list of tuples, [(friend1_id), (friend2_id), ...]
	friends1 = [friend[0] for friend in friends] # list of ints, [friend1_id, friend2_id, ...]

	cursor.execute("SELECT user_id FROM FriendsWith WHERE friend_id = '{0}'".format(uid))
	friends = cursor.fetchall() # list of tuples, [(friend1_id), (friend2_id), ...]	
	friends2 = [friend[0] for friend in friends] # list of ints, [friend1_id, friend2_id, ...]

	friends = friends1 + friends2 # list of user's friends' user IDs, [friend1_id, friend2_id, ...]

	return [getEmailFromUserId(friend) for friend in friends]

#@app.route('/list_friends', methods=['GET', 'POST'])
#@flask_login.login_required
def listFriends():
	user_email = flask_login.current_user.id
	user_id = getUserIdFromEmail(user_email)

	cursor = conn.cursor()
	cursor.execute("""
	SELECT email, firstname, lastname, dob, hometown, gender, score 
	FROM Users, FriendsWith
    WHERE FriendsWith.user_id = '{0}' AND FriendsWith.friend_id = Users.user_id
	UNION
	SELECT email, firstname, lastname, dob, hometown, gender, score 
	FROM Users, FriendsWith
    WHERE FriendsWith.friend_id = '{0}' AND FriendsWith.user_id = Users.user_id
	""".format(user_id))

	table = cursor.fetchall() # list of tuples, each tuple is a row
	rows = [formatAttributes2(list(row)) for row in table] # changes each row to a list instead of a tuple
	recs = getRecFriends(user_email)
	return render_template('list_friends.html', rows=rows, recs=recs)

	

# end friend code


def getphoto():
    cursor=conn.cursor()
    cursor.execute("SELECT (imgdata) FROM Pictures")
    return cursor.fetchall()

@app.route('/browse')
def browse_file():
	cursor = conn.cursor()
	return render_template('hello.html', message='Browse your photo!', photos=getphoto(), base64=base64)

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		#additional inputs
		photo_tags = ''			# for getting multiple tags
		photo_tags_input = request.form.get('tags') 
		if photo_tags_input:
			photo_tags = photo_tags_input.split() # list of tags, split by spaces: "tag1 tag2 tag3" -> ["tag1", "tag2", "tag3"]
		if photo_tags_input:
			photo_tags = photo_tags_input.split() # list of tags, split by spaces: "tag1 tag2 tag3" -> ["tag1", "tag2", "tag3"]
		
		if allowed_file(imgfile):
			album = request.form.get('album')
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Pictures (albums_id, imgdata, user_id, caption, num_likes) VALUES (%s, %s, %s, %s, %s )", \
		  	(album, photo_data, user_id, caption, 0))
			if photo_tags:
				for tag in tags:
					if newTag(tag):
						createTag(tag)
						addTag(tag, picture_id)
			conn.commit
			#update score here when have methods
				
		#cursor = conn.cursor()
		#cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''', (photo_data, user_id, caption))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', \
			 					photos=getUsersPhotos(user_id), base64=base64)
	#The method is GET so we return a HTML form to upload the a photo.
	else:
		return render_template('upload.html')

#helper functions for tags/upload

def newTag(tag):
	cursor = conn.cursor()
	if cursor.execute("SELECT name FROM Tags WHERE word = '{0}'".format(tag)):
		return False
	return True

def createTag(tag): 
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Tags (word, num_photos) VALUES ('{0}', '{1}')".format(tag, 0))
	conn.commit()

# given tag name and photo id, adds a tag to a photo 
def addTag(tag, picture_id): 
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Tagged (picture_id, word, user_id) VALUES ('{0}', '{1}', '{2}')".format(picture_id, tag, user_id))
	conn.commit()
	cursor.execute("UPDATE Tags SET num_photos = num_photos + 1 WHERE word = '{0}'".format(tag)) # updates number of photos associated w tag
	conn.commit()

#Album Code:

@app.route('/album',methods=['GET','POST'])
@flask_login.login_required
def create_album():
	if flask.request.method=='POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('name')
		date = datetime.today().strftime('%Y-%m-%d')  #getting the current date
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Album (name, date, user_id) VALUES (%s, %s, %s)''', (album_name, date, user_id))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Album Created!', album=displayAlbum(), base64=base64)
	else:
		return render_template('create_album.html', name=flask_login.current_user.id)
	
def displayAlbum():
        cursor=conn.cursor()
        cursor.execute("SELECT(name) FROM Album")
        return cursor.fetchall()

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')

def formatAttributes2(userAttributes):
	email, firstname, lastname, dob, hometown, gender, score = userAttributes
	if firstname == "":
		firstname = '-'
	if lastname == "":
		lastname = '-'
	if dob == "0001-01-01":
		dob = '-'
	if hometown == "":
		hometown = '-'
	if gender == "":
		gender = '-'
	return (email, firstname, lastname, dob, hometown, gender, score)

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)


 