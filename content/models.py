from django.db import models
from user.models import User
import datetime

# Create your models here.
class Feed(models.Model):
    content = models.TextField()    # 글내용
    image = models.TextField()  # 피드 이미지
    email = models.EmailField(default='')     # 글쓴이
    create_time = models.DateTimeField(default=datetime.datetime.now())


class Like(models.Model):
    feed_id = models.IntegerField(default=0)
    email = models.EmailField(default='')
    is_like = models.BooleanField(default=True)


class Reply(models.Model):
    feed_id = models.IntegerField(default=0)
    email = models.EmailField(default='')
    reply_content = models.TextField()


class Bookmark(models.Model):
    feed_id = models.IntegerField(default=0)
    email = models.EmailField(default='')
    is_marked = models.BooleanField(default=True)

class VolunteerItem(models.Model):
    admin = models.ForeignKey(User,on_delete = models.CASCADE)
    title = models.TextField(default='')
    volunteer_image = models.TextField()
    region = models.TextField() 
    participant = models.IntegerField(default = 0)
    description = models.TextField()
    lat = models.DecimalField(max_digits = 10,decimal_places= 6, default=0)
    lng = models.DecimalField(max_digits = 10,decimal_places= 6, default=0)
    date = models.DateField(default = None)
    start_time = models.TimeField(default = None)
    end_time = models.TimeField(default = None)
    admit_time = models.IntegerField(default = 0)
    done = models.BooleanField(default=False)
    create_time = models.DateTimeField(default=datetime.datetime.now())

class ParticipateItems(models.Model):
    grant = models.BooleanField(default=False)
    volunteerItem = models.ForeignKey(VolunteerItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)