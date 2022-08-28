from django.urls import path
from .views import DeleteVolunteer, SearchResult, UploadFeed, Profile,\
    Community, UploadReply, ToggleLike, ToggleBookmark, DeleteFeed, createVolunteerITem, \
        Main, Search, Follow, Participate, NotParticipate, feed_detail, volunteer_detail, get_update_feed, PutFeed, profiledetail
from . import views


app_name = 'content'

urlpatterns = [
    path('', Main.as_view(), name="main"),
    path('community', Community.as_view(), name="community"),
    path('profile', Profile.as_view(), name="profile"),
    path('search', Search.as_view(), name="search"),
    path('search_result',  SearchResult.as_view(), name="search_result"),

    path('createvolunteer', createVolunteerITem.as_view(), name="create_volunteer"),
    path('deletevolunteer', DeleteVolunteer.as_view()),

    path('delete_feed', DeleteFeed.as_view()),
    path('upload_feed', UploadFeed.as_view()),
    path('reply_feed', UploadReply.as_view()),
    path('get_update_feed/<int:feed_id>', get_update_feed),
    path('put_update_feed', PutFeed.as_view()),
    path('like_feed', ToggleLike.as_view()),
    path('feed_detail/<int:feed_id>', feed_detail),
    path('volunteer_detail/<int:feed_id>', volunteer_detail),
    path('profile_detail/<int:user_id>', profiledetail),

    path('follow', Follow.as_view(), name="folow"),

    path('bookmark_volunteer', ToggleBookmark.as_view()),
    path('participate_volunteer', Participate.as_view()),
    path('not_participate_volunteer', NotParticipate.as_view()),
]

