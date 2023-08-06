import django.db.models
from django.contrib.contenttypes.models import ContentType


class Label(django.db.models.Model):
    """The name under which a remix gets bound into the top-level context object."""
    label = django.db.models.CharField(max_length=255, 
                               help_text="""
This should be all word-chars ([a-zA-Z0-9_]+) since it'll be available 
as a context field in the templates.""")

    def __unicode__(self):
        return self.label


class SubclassingQuerySet(django.db.models.query.QuerySet):
    """This takes elements of the base type and calls .as_leaf_class() on them.

    We use this as a mechanism to allow a superclass Manager to query for all
    instances and get them back as declared subclass instances.

    Note that in order to complete this correctly, .as_leaf_class() must
    work as expected in the subclass instances."""
    def __getitem__(self, k):
        result = super(SubclassingQuerySet, self).__getitem__(k)
        if isinstance(result, django.db.models.Model) :
            return result.as_leaf_class()
        else :
            return result

    def __iter__(self):
        for item in super(SubclassingQuerySet, self).__iter__():
            yield item.as_leaf_class()


class RemixManager(django.db.models.Manager):
    """Define a custom manager for Remixes that leverages SubclassingQuerySet"""
    def get_query_set(self):
        return SubclassingQuerySet(self.model)


class AbstractRemix(django.db.models.Model):
    class Meta:
        abstract = True

    """The base class for all remixes."""
    descriptor = django.db.models.CharField(max_length=255, help_text="This remix will apply to all request.paths that have this as a prefix.")
    label = django.db.models.ForeignKey(Label)

    def render(self):
        return self

    def __unicode__(self):
        return "%s for %s" % (self.label, self.descriptor)

    def save(self, *args, **kwargs):
        if not self.descriptor.endswith('/'):
            self.descriptor += '/'
        return super(AbstractRemix, self).save(*args, **kwargs)

class Remix(AbstractRemix):
    "A concrete base class to leverage when creating remixes via inheritance."
    content_type = django.db.models.ForeignKey(ContentType,editable=False,null=True)
    objects = RemixManager()

    def save(self, *args, **kwargs):
        if (not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        return super(Remix, self).save(*args, **kwargs)
        #self.save_base(*args, **kwargs)

    def as_leaf_class(self):
        content_type = self.content_type
        model = content_type.model_class()
        if (model == Remix):
            return self
        return model.objects.get(id=self.id)



