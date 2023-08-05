from django.shortcuts import render_to_response
from django.template.context import RequestContext

def time_of_day(request):
    return render_to_response('time_of_day.html', RequestContext(request))
