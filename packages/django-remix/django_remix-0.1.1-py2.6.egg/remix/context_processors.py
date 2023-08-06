from remix import get_remixes

def remix(request):
    "Adds any defined remixes to the context based on matching request.path."
    #raise Exception('processing remix result=%s' % str(get_remixes(request)))
    return get_remixes(request)
