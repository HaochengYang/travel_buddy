from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib import messages
from .models import User, Trip

###################Start render routes####################

def logreg(request):
    return render(request, 'travelbuddy/index.html')

def dashboard(request):
    if not request.session['loggedin']:
        return redirect(reverse('travelbuddy:logreg'))
    context = {
        'user' : request.session['user'],
        'trips' : Trip.objects.filter(Q(planner__id = request.session['user'].id) | Q(joins__id = request.session['user'].id)).order_by('start_date'),
        'others' : Trip.objects.all().exclude(planner__id = request.session['user'].id).exclude(joins__id = request.session['user'].id).order_by('start_date'),
    }
    return render(request, 'travelbuddy/dashboard.html', context)

def destination(request, id):
    if not request.session['loggedin']:
        return redirect(reverse('travelbuddy:logreg'))
    context = {
        'trip' : Trip.objects.get(id = id),
    }
    return render(request, 'travelbuddy/destination.html', context)

def adddest(request):
    if not request.session['loggedin']:
        return redirect(reverse('travelbuddy:logreg'))
    return render(request, 'travelbuddy/addtrip.html')

####################End render routes#####################


##################Start redirect routes###################

def validate(request, typelogin):
    result = User.objects.validator(request.POST, typelogin)
    request.session['loggedin'] = result['loggedin']

    if request.session['loggedin']:
        request.session['user'] = result['user']

    else:
        for regerror in result['errors']['reg']:
            messages.error(request, regerror)
        for logerror in result['errors']['login']:
            messages.warning(request, logerror)

    return redirect(reverse('travelbuddy:dashboard'))

def jointrip(request, id):
    Trip.objects.joiner(id, request.session['user'])
    return redirect(reverse('travelbuddy:dashboard'))

def createtrip(request):
    result = Trip.objects.validator(request.POST, request.session['user'])

    if result['created']:
        return redirect(reverse('travelbuddy:dashboard'))

    else:
        for error in result['errors']:
            messages.error(request, error)
            return redirect(reverse('travelbuddy:adddest'))

def logout(request):
    request.session['loggedin'] = False
    del request.session['user']
    return redirect(reverse('travelbuddy:logreg'))

###################End redirect routes####################
