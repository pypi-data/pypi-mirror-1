# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from remix import *
from remix.models import *

def dashboard(request, url):
    "Renders a dashboard for the given URL to show how remixes were selected."

    labels = []

    #  We lose the leading / of our path url in making urls.py consistent 
    #  with normal conventions so we'll add it back here.
    url = "/" + url

    #  Build a list-of-lists for displaying the dashboard
    for type in Label.objects.order_by("label"):
        labels.append({ 
                'url': url, 
                'label': type.label, 
                'candidates': find_remix_candidates(url, type.label) 
                })

    return render_to_response('remix/dashboard.html', 
                              {  'url': url, 
                                 'labels' : labels },
                              context_instance=RequestContext(request))
