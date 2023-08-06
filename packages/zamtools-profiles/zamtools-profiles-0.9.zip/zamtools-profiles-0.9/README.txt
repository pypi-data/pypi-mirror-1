Django application for creating member profiles for users and grouping them into teams.  The member profiles are intentionally loosely coupled to users, this allows profiles to exist for users that aren't in the system.

= Benefits =

 * Member profiles can be grouped into multiple teams
 * Member profiles can be made private
 * Resizable and cached profile picture
 * Ready-made templates
 * Tests included

= Dependencies = 

 * [http://www.pythonware.com/products/pil/ Python Image Library (PIL)]
 * [http://code.google.com/p/django-photologue/downloads/list Photologue 2.2]
 * [http://www.djangoproject.com Django 1.0]

= Installation =

*NOTE: These steps assume that PIL is already installed.*

== Installing Photologue ==

Photologue is necessary to do image resizing and caching for the member profile pictures. Download Photologue 2.2 and run the following command in the download directory.

{{{
> python setup.py install
}}}

If you have setuptools installed, you can use easy_install instead.

{{{
> easy_install django-photologue
}}}

In your Django project, add Photologue to the INSTALLED_APPS settings.py file.

{{{
INSTALLED_APPS = (
    'photologue',
)
}}}

You can optionally specify where you want Photologue to save uploaded images to, relative to your MEDIA_ROOT, using the PHOTOLOGUE_DIR variable in settings.py.  By default, this is set to 'photologue'.

{{{
PHOTOLOGUE_DIR = 'images'
}}}

The preceding would result in files being saved in `/media/images/` assuming `media` is your MEDIA_ROOT.

Synchronize the database to create the Photologue tables.

{{{
> python manage.py syncdb
}}}

Initialize Photologue to create all necessary defaults.

{{{
> python manage.py plinit
}}}

You will then be prompted with a series of questions to fill in the defaults.  Use the following settings:

{{{
Photologue requires a specific photo size to display thumbnail previews in the Django admin application.

Would you like to generate this size now? (yes, no): yes

We will now define the "admin_thumbnail" photo size:

Width (in pixels): 200 
Height (in pixels): 200 
Crop to fit? (yes, no): yes 
Pre-cache? (yes, no): yes 
Increment count? (yes, no): no 

A "admin_thumbnail" photo size has been created.

Would you like to apply a sample enhancement effect to your admin thumbnails? (yes, no): no

Photologue comes with a set of templates for setting up a complete photo gallery. These templates require you to define both a "thumbnail" and "display" size.

Would you like to define them now? (yes, no): yes

We will now define the "thumbnail" photo size:

Width (in pixels): 200
Height (in pixels): 200
Crop to fit? (yes, no): yes
Pre-cache? (yes, no): yes
Increment count? (yes, no): no

A "thumbnail" photo size has been created.

We will now define the "display" photo size:

Width (in pixels): 600
Height (in pixels): 600
Crop to fit? (yes, no): yes
Pre-cache? (yes, no): yes
Increment count? (yes, no): no

A "display" photo size has been created.

Would you like to apply a sample reflection effect to your display images? (yes, no): no
}}}

Create a custom PhotoSize for the member profile picture called "avatar".

{{{
> python manage.py plcreatesize avatar
}}}

You will then be prompted with a series of questions to fill in the defaults.  Use the following settings:

{{{
We will now define the "avatar" photo size:

Width (in pixels): 100
Height (in pixels): 150
Crop to fit? (yes, no): yes
Pre-cache? (yes, no): yes
Increment count? (yes, no): no

A "avatar" photo size has been created.
}}}

== Installing zamtools-profiles ==

If you have setuptools installed, you can use easy_install.

{{{
> easy_install zamtools-profiles
}}}

Add zamtools-profiles to the INSTALLED_APPS list in settings.py.

{{{
INSTALLED_APPS = (
    'photologue',
    'profiles',
)
}}}

Synchronize the database.

{{{
> python manage.py syncdb
}}}

If you want to use the ready-made views and templates include the following url pattern in urls.py.

{{{
urlpatterns = patterns('', 
    (r'^profiles/', include('profiles.urls')),
)
}}}

= Usage =

Login to the admin interface and add a Member and assign it an image.

Create a Team and assign your Member to it.

The Member model has a `public` manager for retriving only members who's `is_public` field is set to True.

{{{
public_members = Members.public.all()
}}}

The Member model has an `image()` convenience method for retrieving the latest `MemberImage` assigned to it.

{{{
member = Member.public.get(id=1)
member_image = member.image()
member_image.get_avatar_url()
}}}

The image can be retrieved in a template using the following.

{{{
<div class="member">
    <h1>{{ member }}</h1>
    <img src="{{ member.image.get_avatar_url }}" />
</div>
}}}

The Team model has a `public_members()` convenience method for retrieving only those members on the team who's `is_public` field is set to True.