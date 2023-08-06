from django.template import RequestContext
from django.shortcuts import render_to_response
from models import *

def index(request, extra_context={}, template_name='profiles/index.html'):
    # get all members that don't belong to a group
    orphan_members = Member.public.filter(team=None)
    teams = Team.objects.all()
    return render_to_response(template_name, {'teams':teams, 'orphan_members':orphan_members}, context_instance=RequestContext(request))