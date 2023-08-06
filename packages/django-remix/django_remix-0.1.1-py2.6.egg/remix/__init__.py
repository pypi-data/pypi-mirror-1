try:
    from django.db.models import Q
except:
    print 'must be building'

from remix.models import *

__version__ = "0.1.1"    

class RemixRegistry:
    """
    A simple managed list of remix object models that we need to load
    when looking for matches.

    For folks who aren't keen on our use of non-abstract inheritance,
    this gives you an out.  Simply call remix.registry.register(model)
    where model is the model type (e.g. Remix).
    """
    def __init__(self):
        self.registered_types = {}

        
    def filter(self, *args, **kwargs):
        """Aggregating 'shim' for underlying model queries.

        Note that this presumes that any headers required by the overall
        search algorithm are available for any registered type!

        Read: Don't get cute and call label something else in your
        remix type!"""

        matches = []
        for name, model in self.registered_types.items():
            try:
                list = model.objects.filter(*args, **kwargs)
                matches.extend(list)
            except Exception, e:
                print "Failed to marshall", name, "remixes: ", e

        return matches


    def register(self, model):
        """Stash a handle to every registered model type object.
        
        We'll later iterate over these looking for matches to our """
        self.registered_types[str(model)] = model
        
        #  Return self, to enable chaining (for what it's worth here)
        return self


#  Declare a singleton remix registry...
registry = RemixRegistry()

#  For legacy compatibility, preload the base Remix type, which gets
#  any subclasses.
#
#  Note that only non-subclasses of Remix need to register.
registry.register(Remix)



#  TODO  Perhaps all of these functions should move into RemixRegistry

#  This is a separate function so that views.dashboard can enumerate
#  all the possible matches in order of preference.
def remix_resolver(request, label):
    """Loads all of the possible matches for this tuple and returns an
    ordered list.
    
    In the first incarnation, this is done with longest-match-wins logic
    rather than anything fancier.  
    
    The key assumption here is that as you work through the tree of pages
    for a site, a page's logical "parent" in the site (e.g. a section page
    v. an article) will always have a url that's a substring of its
    children.
    
    """
    #  Load all of the remixes for the provided label...
    path_parts = [part for part in request.path.split('/') if part!='']
    q = Q(descriptor='/')
    for x in range(1,len(path_parts)+1):
         q = q | Q(descriptor='/%s/' % '/'.join(path_parts[:x]))
    
    remixes = list(registry.filter(q, label__label=label))
    
    #  Find anything that is a substring of our URL
    #matches = filter(lambda b: request.path.startswith(b.descriptor), remixes)

    #  Sort them by length of descriptor, descending
    remixes.sort(lambda l, r: cmp(len(r.descriptor), len(l.descriptor)))

    return remixes


def find_remix(request, label):
    """Loads the most specific remix for this label, request pair.
"""
    matches = remix_resolver(request, label)

    #  Note that matches is sorted best-match to worst.
    if len(matches) > 0:
        return matches[0]
    else:
        raise LookupError("No remix found for (%s, %s)" % (request, label))


def get_remixes(request):
    """Retrieves all of the remixes associated with the provided
HttpRequest."""

    remixes = {}

    for label in Label.objects.all():
        try:
            remixes[label.label] = find_remix(request, label.label).render()
        except LookupError:
            #  Not having a remix defined for each Label isn't
            #  currently an error.
            pass

    return remixes


