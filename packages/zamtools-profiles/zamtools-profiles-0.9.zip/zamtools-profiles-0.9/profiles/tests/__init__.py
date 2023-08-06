from django.test import TestCase
from django.core.files.base import ContentFile
from django.db import models
from photologue.models import ImageModel, PhotoSize
from ..models import Member, Team
from django.core.files import File
import os
import settings

class PublicTests(TestCase):
    def setUp(self):
        self.public_member = Member.objects.create(first_name='Public', last_name='Member', is_public=True)
        self.private_member = Member.objects.create(first_name='Private', last_name='Member', is_public=False)
        self.members = [self.public_member, self.private_member]
        self.team = Team.objects.create(name='Team')
        self.team.members = self.members
        self.team.save()

    def tearDown(self):
        self.team.delete()
        for member in self.members:
            member.delete()

    def test_public_manager(self):
        public_members = Member.public.all()
        self.assertEqual(list(public_members), [self.public_member])

    def test_team_public_members(self):
        self.assertEqual(list(self.team.public_members()), [self.public_member])

class ContextTests(TestCase):
    urls = 'profiles.tests.urls'

    def setUp(self):
        self.public_member = Member.objects.create(first_name='Public', last_name='Member', is_public=True)
        self.orphan_member = Member.objects.create(first_name='Public', last_name='Member', is_public=True)
        self.members = [self.public_member, self.orphan_member]
        self.team = Team.objects.create(name='Team')
        self.team.members = [self.public_member]
        self.team.save()

    def tearDown(self):
        self.team.delete()
        for member in self.members:
            member.delete()

    def test_team_members(self):
        response = self.client.get('/profiles/')
        self.assertEqual(list(response.context[0]['teams'][0].public_members()), [self.public_member])

    def test_orphan_members(self):
        response = self.client.get('/profiles/')
        self.assertEqual(list(response.context[0]['orphan_members']), [self.orphan_member])

RES_DIR = os.path.join(os.path.dirname(__file__), 'resources')
MEMBER_IMAGE_PATH = os.path.join(RES_DIR, 'test_sample.jpg')

class MemberImage(ImageModel):
    """ Minimal ImageModel class for testing """
    name = models.CharField(max_length=50)
    member = models.ForeignKey(Member)
    
    def __inicode__(self):
        return self.name

class ImageTests(TestCase):
    def setUp(self):
        self.photo_size = PhotoSize(name='test', width=100, height=100)
        self.photo_size.save()
        self.member = Member.objects.create(first_name='Public', last_name='Member', is_public=True)
        self.member_images = []

    def tearDown(self):
        for member_image in self.member_images:
            path = member_image.image.path
            member_image.delete()
            self.failIf(os.path.isfile(path))
        self.photo_size.delete()
        self.member.delete()

    def test_no_image(self):
        self.assertEqual(self.member.image(), None)

    def test_one_image(self):
        member_image = MemberImage(member=self.member)
        member_image.name = 'first'
        member_image.image.save(os.path.basename(MEMBER_IMAGE_PATH), ContentFile(open(MEMBER_IMAGE_PATH, 'rb').read()))
        member_image.save()
        self.member_images.append(member_image)
        self.assertEqual(self.member.image(), member_image)

    def test_two_images(self):
        first_image = MemberImage(member=self.member)
        first_image.name = 'first'
        first_image.image.save(os.path.basename(MEMBER_IMAGE_PATH), ContentFile(open(MEMBER_IMAGE_PATH, 'rb').read()))
        first_image.save()
        self.member_images.append(first_image)
        second_image = MemberImage(member=self.member)
        second_image.name = 'second'
        second_image.image.save(os.path.basename(MEMBER_IMAGE_PATH), ContentFile(open(MEMBER_IMAGE_PATH, 'rb').read()))
        second_image.save()
        self.assertEqual(self.member.image(), second_image)
