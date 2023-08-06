from django.db import models
from django.contrib.auth.models import User
from photologue.models import ImageModel
from fields import AutoSlugField

class PublicManager(models.Manager):
    """
    Returns only members where is_public is True.
    """
    def get_query_set(self):
        return super(PublicManager, self).get_query_set().filter(is_public=True)

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50, null=True, blank=True, help_text='Optionally specify the person\'s position. eg: CEO, Manager, Developer, etc.')
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, help_text='Optionally associate the profile with a user.')
    order = models.IntegerField(default=0, null=True, blank=True, help_text='Optionally specify the order profiles should appear. Lower numbers appear sooner. By default, profiles appear in the order they were created.')
    is_public = models.BooleanField(default=True, null=True, blank=True, help_text='Profile can be seen by anyone when checked.')
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    public = PublicManager()

    def image(self):
        """
        Convenience method for returning the single most recent member image.
        """
        member_images = self.memberimage_set.all()
        if member_images:
            return member_images[0]

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    class Meta:
        ordering = ['-order', '-date_created', 'id']

class MemberImage(ImageModel):
    member = models.ForeignKey(Member)
    
    class Meta:
        ordering = ['-id']

class Team(models.Model):
    name = models.CharField(max_length=50)
    slug = AutoSlugField(overwrite_on_save=True)
    description = models.TextField(null=True, blank=True)
    members = models.ManyToManyField(Member, null=True, blank=True)
    order = models.IntegerField(default=0, null=True, blank=True, help_text='Optionally specify the order teams should appear. Lower numbers appear sooner. By default, teams appear in the order they were created.')
    date_created = models.DateTimeField(auto_now_add=True)

    def public_members(self):
        """
        Convenience method for returning only members of the team who's 
        is_public is True.
        """
        return self.members.filter(is_public=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-order', '-date_created', 'id']