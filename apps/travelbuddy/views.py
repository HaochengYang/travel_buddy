from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib import messages
from .models import User, Trip

###################Start render routes####################

def logreg(request): #renders login/register page
    return render(request, 'travelbuddy/index.html')

def dashboard(request): #renders dashboard
    if not request.session['loggedin']: #if the user is not logged in...
        return redirect(reverse('travelbuddy:logreg')) #redirect them to the login page
    context = {
        'username' : request.session['user'].username, #passes username in context
        'trips' : Trip.objects.filter(Q(planner__id = request.session['user'].id) | Q(joins__id = request.session['user'].id)).order_by('start_date'), #trip query filters trips the user is a planner of and the ones they have joined in on and orders them by the soonest
        'others' : Trip.objects.all().exclude(planner__id = request.session['user'].id).exclude(joins__id = request.session['user'].id).order_by('start_date'), #trip query to store trips that the user isn't planning on attending
    }
    return render(request, 'travelbuddy/dashboard.html', context)

def destination(request, id): #renders appropriate destination page
    if not request.session['loggedin']: #logged in check...
        return redirect(reverse('travelbuddy:logreg'))
    context = {
        'trip' : Trip.objects.get(id = id), #retrieves the specific trip details and stores them in trip
    }
    return render(request, 'travelbuddy/destination.html', context)

def adddest(request): #renders the add a trip page
    if not request.session['loggedin']: #logged in check...
        return redirect(reverse('travelbuddy:logreg'))
    return render(request, 'travelbuddy/addtrip.html')

####################End render routes#####################


##################Start redirect routes###################

def validate(request, typelogin): #validates the user on login
    result = User.objects.validator(request.POST, typelogin) #sends the entered information to the User validator method in models and stores the returned information in result
    request.session['loggedin'] = result['loggedin'] #session logged in will either be True or False depending on the user's ability to provide the correct information to the login/register page

    if request.session['loggedin']: #if the user is able to successfully log in
        request.session['user'] = result['user'] #store the user's information in session

    else: #if the user is not able to successfully log in...
        for regerror in result['errors']['reg']: #return the register errors
            messages.error(request, regerror)
        for logerror in result['errors']['login']: #return the login errors
            messages.warning(request, logerror)

    return redirect(reverse('travelbuddy:dashboard'))

def jointrip(request, id): #joins a trip to a user
    Trip.objects.joiner(id, request.session['user']) #sends the trip id and user information to the Trip joiner method in models
    return redirect(reverse('travelbuddy:dashboard'))

def createtrip(request): #enters the user's trip information into the database
    result = Trip.objects.validator(request.POST, request.session['user']) #sends the entered information to the Trip validator method in models and stores the returned information in result

    if result['created']: #if the user is able to successfully create a trip...
        return redirect(reverse('travelbuddy:dashboard')) #send them back to the dashboard

    else: #if the user is not able to successfully create a trip...
        for error in result['errors']: #return the errors
            messages.error(request, error)
            return redirect(reverse('travelbuddy:adddest')) #send the user back to the add destination page

def logout(request): #logs the user out
    request.session['loggedin'] = False #sets logged in status to false
    del request.session['user'] #deletes the user's information from session
    return redirect(reverse('travelbuddy:logreg'))

###################End redirect routes####################
