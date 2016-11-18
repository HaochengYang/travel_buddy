from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import re, bcrypt

class UserManager(models.Manager):
	def validator(self, postData, typelogin): #validates login/registration informtaion
		NAME_REGEX = re.compile(r'^[a-zA-Z]{3,}\s*[a-zA-Z\-\']+$')
		USERNAME_REGEX = re.compile(r'(?=^.{3,}$)(?=.*\d)*(?=.*[a-z])*(?=.*[A-Z])*(?=.*[!@#$%^&amp;*()_+}{&quot;:;\'?/&gt;.&lt;,])*(?!.*\s)*.*$')
		PWORD_REGEX = re.compile(r'(?=^.{8,}$)(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&amp;*()_+}{&quot;:;\'?/&gt;.&lt;,])(?!.*\s).*$')
		errors = {
			'reg' : [],
			'login' : [],
		} #empty dictionary to push errors to for registration, password, and login attempts
		result = {} #empty dictionary to store return values

		if typelogin == 'register': #if the user is trying to register...
			try: #attempt to retrieve user information based on the username they entered
				validuser = self.get(username = postData['username'])
			except User.DoesNotExist: #set validuser to none if it isn't able to retrieve anything
				validuser = None

			if validuser: #if able to retrieve a user from the database based on the entered username address...
				errors['reg'].append('This username has already been registered.')
			if '' in (postData['name'], postData['username'], postData['password'], postData['confirm']): #if any of the fields are left blank...
				errors['reg'].append('Please fill in all fields.')
			if not NAME_REGEX.match(postData['name']): #if the name isn't a valid format
				errors['reg'].append('Please enter a valid name (Must be at least 3 characters in length and include a first and last name).')
			if not USERNAME_REGEX.match(postData['username']): #if the username isn't a valid format
				errors['reg'].append('Please enter a valid username (Must be at least 3 characters in length).')
			if not PWORD_REGEX.match(postData['password']): #if the password doesn't meet the minimum requirements
				errors['reg'].append('Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character.')
			if postData['password'] != postData['confirm']: #if the password and password confirmation don't match
				errors['reg'].append('Password and confirmation password do not match.')

		elif typelogin == 'login': #if the user is trying to login...
			try: #attempt to retrieve the user information based on the entered username address
				loginuser = self.get(username = postData['username'])
			except User.DoesNotExist: #if the entered username address isn't in the system, set loginuser to none
				loginuser = None

			if not loginuser: #if the entered username address isn't in the database...
				errors['login'].append('Please enter a registered username and/or valid password.')
			elif not bcrypt.hashpw(postData['password'].encode(), loginuser.password.encode()) == loginuser.password.encode(): #if the password doesn't match the one for the user in the database...
				errors['login'].append('Please enter a registered username and/or valid password.')

		if not errors['reg'] and not errors['login']: #if there are no errors...
			if typelogin == 'register': #and the user is registering
				user = self.creator(postData) #create the user using the creator method below and store the user information returned as user
			elif typelogin == 'login': #if the user is logging in
				user = self.get(username = postData['username']) #retrieve that user's information and store is as user
			result['loggedin'] = True #set the user's logged in status to true and store it in the result dictionary
			result['user'] = user #store the user information in the result dictionary

		else: #however, if there ARE errors...
			result['loggedin'] = False #set the user's logged in status to false and store it in the result dictionary
			result['errors'] = errors #store the errors in the result dictionary

		return result #return the result dictionary

	def creator(self, data): #creates the user in the database based on the appropriately entered registration information
		new_user = self.create(name = data['name'], username = data['username'], password = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()))
		return new_user #return the newly created user's information

class TripManager(models.Manager):
	def validator(self, tripData, user): #validates the entered trip information
		errors = [] #creates an empty list for errors
		result = {} #creates an empty dictionary for the result
		today = datetime.now() #creates a variable for today's date/time

		try: #try to convert the user's entered date to something that we can compare the today variable to
			start = datetime.strptime(tripData['start_date'], "%Y-%m-%d")
			end = datetime.strptime(tripData['end_date'], "%Y-%m-%d")

			if start < today: #if the trip start_date is before today...
				errors.append('All dates need to be after today.')
			if end < start: #if the trip end_date is before the start_date...
				errors.append('Please ensure your travel date from is before your travel date to.')

		except ValueError: #if a ValueError is thrown because either of the datefields are left blank...
			pass

		if '' in (tripData['destination'], tripData['plan'], tripData['start_date'], tripData['end_date']): #if any of the fields are left blank...
			errors.append('Please fill in all fields.')

		if not errors: #if there are no errors after being validated...
			self.creator(tripData, user) #send the entered information along with the user information to the Trip creator method
			result['created'] = True #set created to True

		else: #if there are errors...
			result['created'] = False #set created to False
			result['errors'] = errors #store the errors in result

		return result

	def creator(self, data, user): #creates the new trip based on the user entered information
		self.create(destination = data['destination'], plan = data['plan'], start_date = data['start_date'], end_date = data['end_date'], planner = user)
		return self

	def joiner(self, trip_id, user): #joins a particular trip to a user
		trip = self.get(id = trip_id)
		trip.joins.add(user)
		return self

class User(models.Model):
	name = models.CharField(max_length = 255)
	username = models.CharField(max_length = 255)
	password = models.CharField(max_length = 255)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = UserManager()

class Trip(models.Model):
	destination = models.CharField(max_length = 255)
	plan = models.TextField(max_length = 1000)
	start_date = models.DateField(auto_now = False, auto_now_add = False)
	end_date = models.DateField(auto_now = False, auto_now_add = False)
	planner = models.ForeignKey(User, related_name = 'trip')
	joins = models.ManyToManyField(User, related_name = 'joined')
	objects = TripManager()
