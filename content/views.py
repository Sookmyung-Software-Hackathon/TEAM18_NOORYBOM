from uuid import uuid4
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Feed, ParticipateItems, Reply, Like, Bookmark, VolunteerItem
from user.models import User
import os
from Jinstagram.settings import MEDIA_ROOT
from django.db.models import Q
from content.models import VolunteerItem
from django.views.decorators.csrf import csrf_exempt
from . import config
import math
import collections
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

class Community(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        mainuser = User.objects.filter(email=email).first()

        if mainuser is None:
            return render(request, "user/login.html")

        feed_object_list = Feed.objects.all().order_by('-id')  # select  * from content_feed;
        feed_list = []

        volunteer_object_list = VolunteerItem.objects.all().order_by('-id')
        volunteer_list = []

        for feed in feed_object_list:
            user = User.objects.filter(email=feed.email).first()
            reply_object_list = Reply.objects.filter(feed_id=feed.id)
            reply_list = []
            for reply in reply_object_list:
                reply_user = User.objects.filter(email=reply.email).first()
                reply_list.append(dict(reply_content=reply.reply_content,nickname=reply_user.nickname))
            like_count=Like.objects.filter(feed_id=feed.id, is_like=True).count()
            is_liked=Like.objects.filter(feed_id=feed.id, email=email, is_like=True).exists()
            feed_list.append(dict(id=feed.id,
                                email = feed.email,
                                image=feed.image,
                                content=feed.content,
                                like_count=like_count,
                                profile_image=user.profile_image,
                                nickname=user.nickname,
                                reply_list=reply_list,
                                is_liked=is_liked,
                                create_time = feed.create_time
                                ))

        for volunteer in volunteer_object_list:
            is_marked=Bookmark.objects.filter(feed_id=volunteer.id, email=email, is_marked=True).exists()
            participateitems = ParticipateItems.objects.filter(volunteerItem_id =volunteer.id).all() # 참여 신청 리스트 중 해당 봉사에 해당하는 것들
            participateitem = participateitems.filter(user_id = mainuser.id).first() # 그 중에서 현재 로그인된 유저가 신청한 것들
            isparticipated = False
            grant = False
            if participateitem:
                grant = participateitem.grant
                isparticipated = True
            print(isparticipated)

            volunteer_list.append(dict(id=volunteer.id,
                                image=volunteer.volunteer_image,
                                region=volunteer.region,
                                participant=volunteer.participant,
                                admin = volunteer.admin,
                                isparticipated = isparticipated,
                                grant = grant,
                                is_marked = is_marked,
                                create_time = volunteer.create_time,
                                title = volunteer.title,
                                ))



        return render(request, "content/community.html", context=dict(feeds=feed_list, 
                                                                    volunteers = volunteer_list,
                                                                    mainuser=mainuser))

class Participate(APIView):
    def post(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()

        volunteer_id = request.data.get('volunteer_id')
        participated_item = VolunteerItem.objects.filter(id=volunteer_id).first()

        print(volunteer_id)
        print(participated_item)

        ParticipateItems.objects.create(
            user_id = mainuser.id,
            volunteerItem_id = participated_item.id,
            grant=0
        )
        participated_item.participant-=1
        participated_item.save()

        return Response(200)

class NotParticipate(APIView):
    def delete(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()

        volunteer_id = request.data.get('volunteer_id')
        participated_item = VolunteerItem.objects.filter(id=volunteer_id).first()
        print(participated_item.participant)
        participated_item.participant = participated_item.participant + 1
        participated_item.save()

        remove_item = ParticipateItems.objects.filter(Q(user_id = mainuser.id) & Q(volunteerItem_id = participated_item.id))
        remove_item.delete()

        return Response(200)

class UploadFeed(APIView):
    def post(self, request):

        # 일단 파일 불러와
        file = request.FILES['file']

        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        asdf = uuid_name
        content123 = request.data.get('content')
        email = request.session.get('email', None)

        Feed.objects.create(image=asdf, content=content123, email=email)

        return Response(status=200)

class DeleteFeed(APIView):
    def delete(self, request):
        feed_id = request.data.get('feed_id', None)
        feed = Feed.objects.filter(id=feed_id).first()
        feed.delete()
        return Response(status=200)


class Profile(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")

        mainuser = User.objects.filter(email=email).first()

        if mainuser is None:
            return render(request, "user/login.html")

        participate_list=[]
        participated_user_list=[]


        if mainuser.role =='Admin':
            created_list = VolunteerItem.objects.filter(admin=mainuser).all()
            for item in created_list: # 봉사 기관자가 생성한 voluteeritem에 대해서
                participated_created_list = ParticipateItems.objects.filter(volunteerItem_id = item.id).all() # 신청된 것들 선발
                if participated_created_list: #만약 신청 받은 것이 있다면
                    for participated_item in participated_created_list:
                        user = User.objects.filter(id = participated_item.user_id).first()
                        isgranted = participated_item.grant
                        participate_list.append([item, user, isgranted])
        else:
            participated_list =[]
            participated_list.append(ParticipateItems.objects.filter(user_id = mainuser.id).all()) # 현재 유저가 신청한 volunteeritem들
            for i in participated_list:
                print(i)
                for participated_item in i:
                    print(participated_item)
                    if(participated_item):
                        participate_item = VolunteerItem.objects.filter(id = participated_item.volunteerItem_id) # 직접 volunteeritem 객체 배열에 넣어주기
                        if participate_item:
                            grant = ParticipateItems.objects.filter(volunteerItem_id = participate_item.first().id).first().grant # 해당 봉사의 승인 여부
                            participate_list.append([participate_item, grant])

        feed_list = Feed.objects.filter(email=email)
        like_list = list(Like.objects.filter(email=email, is_like=True).values_list('feed_id', flat=True))
        like_feed_list = Feed.objects.filter(id__in=like_list)
        bookmark_list = list(Bookmark.objects.filter(email=email, is_marked=True).values_list('feed_id', flat=True))
        bookmark_volunteer_list = VolunteerItem.objects.filter(id__in=bookmark_list)

        user_list = User.objects.order_by('id')
        return render(request, 'content/profile.html', context=dict(feed_list=feed_list,
                                                                    like_feed_list=like_feed_list,
                                                                    bookmark_volunteer_list=bookmark_volunteer_list,
                                                                    mainuser = mainuser,
                                                                    participate_list=participate_list,
                                                                    user_list =user_list
                                                                ))

    def post(self, request):
        user = request.data.get('user')
        item = request.data.get('item')
        time = request.data.get('admit_time')

        granted_user = User.objects.filter(id=user).first()
        granted_user.sum_time += int(time)

        if granted_user.sum_time >=20 :
            granted_user.ranking = 'Flower🌸'
        elif granted_user.sum_time >=15 :
            granted_user.ranking = 'Tree🌲'
        elif granted_user.sum_time >=10 :
            granted_user.ranking = 'Seedling🍃'
        elif granted_user.sum_time >=5 :
            granted_user.ranking = 'Sprout🌱'

        granted_user.save()

        granted_item = ParticipateItems.objects.filter(volunteerItem_id=item).first()
        granted_item.grant = 1
        granted_item.save()

        remove_item = ParticipateItems.objects.filter(Q(user_id = user) & Q(volunteerItem_id = item))
        remove_item.delete()


        return Response(status=200)


class UploadReply(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        reply_content = request.data.get('reply_content', None)
        email = request.session.get('email', None)

        Reply.objects.create(feed_id=feed_id, reply_content=reply_content, email=email)

        return Response(status=200)


class ToggleLike(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id', None)
        favorite_text = request.data.get('favorite_text', True)

        if favorite_text == 'favorite_border':
            is_like = True
        else:
            is_like = False
        email = request.session.get('email', None)

        like = Like.objects.filter(feed_id=feed_id, email=email).first()

        if like:
            like.is_like = is_like
            like.save()
        else:
            Like.objects.create(feed_id=feed_id, is_like=is_like, email=email)

        return Response(status=200)


class ToggleBookmark(APIView):
    def post(self, request):
        volunteer_id = request.data.get('volunteer_id', None)
        bookmark_text = request.data.get('bookmark_text', True)
        print(volunteer_id)
        print(bookmark_text)
        if bookmark_text == 'bookmark_border':
            is_marked = True
        else:
            is_marked = False
        email = request.session.get('email', None)

        bookmark = Bookmark.objects.filter(feed_id=volunteer_id, email=email).first()

        if bookmark:
            bookmark.is_marked = is_marked
            bookmark.save()
        else:
            Bookmark.objects.create(feed_id=volunteer_id, is_marked=is_marked, email=email)

        return Response(status=200)

class Search(APIView):
    def get(self, request):
        email = request.session.get('email', None)

        if email is None:
            return render(request, "user/login.html")
        mainuser = User.objects.filter(email=email).first()

        distance=[]

        volunteer_list = volunteer_list = VolunteerItem.objects.order_by('id')
        Point2D = collections.namedtuple('Point2D', ['x', 'y'])   # namedtuple로 점 표현

        for volunteer in volunteer_list:
            p1 = Point2D(x = volunteer.lat, y = volunteer.lng)
            p2 = Point2D(x = mainuser.lat, y = mainuser.lng)

            a = p1.x - p2.x    # 선 a의 길이
            b = p1.y - p2.y    # 선 b의 길이

            c = math.sqrt((a * a) + (b * b))
            distance.append([c, volunteer.lat, volunteer.lng])

        distance.sort()
        if len(distance) > 5:
            distance = distance[0:6]
        
        volunteer_list=[]
        for d in distance:
            query = VolunteerItem.objects.filter(Q(lat = d[1]) & Q(lng = d[2])).distinct()
            volunteer_list.append(query)
        

        bookmark_volunteer_list=[]
        for set_item in volunteer_list:
            for item in set_item:
                print(item)
                is_marked=Bookmark.objects.filter(feed_id=item.id, email=email, is_marked=True).exists()
                bookmark_item = []
                bookmark_item.append([item, is_marked])
                bookmark_volunteer_list.append(bookmark_item)

        return render(request, "content/search.html", context=dict(mainuser=mainuser,
                                                                    volunteer_list = volunteer_list[:],
                                                                    bookmark_volunteer_list= bookmark_volunteer_list[:]))     

class SearchResult(APIView):
    def get(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()
        volunteer_list = config.volunteer_list


        bookmark_volunteer_list=[]
        for item in volunteer_list:
            print(item)
            is_marked=Bookmark.objects.filter(feed_id=item.id, email=email, is_marked=True).exists()
            bookmark_item = []
            bookmark_item.append([item, is_marked])
            bookmark_volunteer_list.append(bookmark_item)

        return render(request, "content/search.html", context=dict(mainuser=mainuser,
                                                                    bookmark_volunteer_list=bookmark_volunteer_list))   
    def post(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()
        volunteer_list = VolunteerItem.objects.order_by('id')
        search_item = request.data.get('search_item', None)
        volunteer_list = volunteer_list.filter(
            Q(description__contains=search_item) | 
            Q(title__contains=search_item)
        ).distinct()
        config.volunteer_list = volunteer_list
        print(volunteer_list)

        bookmark_volunteer_list=[]
        for item in volunteer_list:
            print(item)
            is_marked=Bookmark.objects.filter(feed_id=item.id, email=email, is_marked=True).exists()
            bookmark_item = []
            bookmark_item.append([item, is_marked])
            bookmark_volunteer_list.append(bookmark_item)

        return render(request, "content/search.html", context=dict(mainuser=mainuser,
                                                                    bookmark_volunteer_list=bookmark_volunteer_list))

class createVolunteerITem(APIView):
    def get(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()
        return render(request, "content/createVolunteerItem.html", context=dict( mainuser=mainuser))

    def post(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()
        # 일단 파일 불러

        file = request.data.get('file_give', None)
        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination: 
            for chunk in file.chunks():
                destination.write(chunk)

        image = uuid_name
        region = request.data.get('region', None)
        participant = request.data.get('participant', None)
        description = request.data.get('description', None)
        date = request.data.get('date', None)
        start_time = request.data.get('start_time', None)
        end_time = request.data.get('end_time', None)
        admit_time = request.data.get('admit_time', None)
        admin = request.data.get('admin', None)
        title = request.data.get('title', None)
        lat = request.data.get('lat', None)
        lng = request.data.get('lng', None)
        email = request.data.get('email', None)

        admin = User.objects.filter(email=email).first()
        print(email)
        print(admin)

        VolunteerItem.objects.create(
                            admin = admin,
                            volunteer_image=image, 
                            region = region,
                            participant = participant,
                            description = description,
                            date = date,
                            start_time = start_time,
                            end_time = end_time,
                            admit_time=admit_time,
                            title=title,
                            lat=lat,
                            lng=lng,
                            )

        return Response(status=200)

class DeleteVolunteer(APIView):
    def delete(self, request):
        volunteer_id = request.data.get('volunteer_id', None)
        volunteeritem = VolunteerItem.objects.filter(id=volunteer_id).first()
        volunteeritem.delete()
        return Response(status=200)

class Main(APIView):
    def get(self, request):
        return render(request, "content/main.html")

class Follow(APIView):
    def get(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()
        user_list = User.objects.order_by('id')
        
        return render(request, "content/profile.html",context=dict(user_list=user_list, mainuser=mainuser))

    def post(self, request):
        email = request.session.get('email', None)
        mainuser = User.objects.filter(email=email).first()

        follow_email = request.data.get('follow_email', None)
        follow_user = User.objects.filter(email=follow_email).first()
        print(follow_user.id)

        if follow_user in mainuser.followers.all():
            mainuser.followers.remove(follow_user)
        else:
            mainuser.followers.add(follow_user)
        mainuser.save()
        print(mainuser.followers.all())

        return render(request, "content/test.html", context=dict(mainuser=mainuser))



def feed_detail(request, feed_id):
    feed = get_object_or_404(Feed, pk = feed_id)
    user = User.objects.filter(email=feed.email).first()
    reply_object_list = Reply.objects.filter(feed_id=feed.id)
    reply_list = []
    is_liked=Like.objects.filter(feed_id=feed.id, email=user.email, is_like=True).exists()
    print(is_liked)
    for reply in reply_object_list:
        reply_user = User.objects.filter(email=reply.email).first()
        reply_list.append(dict(reply_content=reply.reply_content,nickname=reply_user.nickname))
    context = {"feed": feed, "nickname": user.nickname, "profile_image" : user.profile_image, "reply_list" : reply_list, "is_liked": is_liked}
    return render(request, "content/feed_detail.html", context)

def volunteer_detail(request, feed_id):
    volunteeritem = get_object_or_404(VolunteerItem, pk = feed_id)
    user = User.objects.filter(email=volunteeritem.admin.email).first()
    is_marked=Bookmark.objects.filter(feed_id=volunteeritem.id, email=user.email, is_marked=True).exists()
    context = {"volunteeritem": volunteeritem, "nickname": user.nickname, "profile_image" : user.profile_image, "is_marked" : is_marked}
    return render(request, "content/volunteer_detail.html", context)

def get_update_feed(request, feed_id):
    feed = get_object_or_404(Feed, pk = feed_id)
    user = User.objects.filter(email=feed.email).first()
    reply_object_list = Reply.objects.filter(feed_id=feed.id)
    reply_list = []
    is_liked=Like.objects.filter(feed_id=feed.id, email=user.email, is_like=True).exists()
    for reply in reply_object_list:
        reply_user = User.objects.filter(email=reply.email).first()
        reply_list.append(dict(reply_content=reply.reply_content,nickname=reply_user.nickname))
    context = {"feed": feed, "nickname": user.nickname, "profile_image" : user.profile_image, "reply_list" : reply_list, "is_liked": is_liked, "email" : user.email}
    return render(request, "content/feed_update.html", context)

class PutFeed(APIView):
    def put(self, request):
        print(request.data)
        feed_id = request.data.get('feed_id')
        content = request.data.get('content')
        feed = get_object_or_404(Feed, pk = feed_id)
        feed.content = content

        print(feed)
        print(content)

        feed.save()

        return Response(status=200)
