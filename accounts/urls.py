from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from post import views as post_views
urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', obtain_auth_token, name='auth_token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/followers/', views.FollowersView.as_view(), name='profile_follower'),
    path('profile/<slug:username>/following/', views.FollowingView.as_view(), name='profile_following'),
    path('profile/delete/', views.ProfileDeleteView.as_view(), name='profile_delete'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/<slug:username>/', views.ProfileOtherView.as_view(), name='profile_other'),
    path('profile/<slug:username>/follow/', views.FollowView.as_view(), name='follow'),


    #views from post app
    path('posts/', post_views.ProfilePostListView.as_view(), name='profile-post-list'),
    path('profile/post/<int:pk>/', post_views.ProfilePostDetailView.as_view(), name='profile_post_detail'),
    path('profile/<slug:username>/post/', post_views.ProfileOtherPostListView.as_view(), name='profile_other_post_list'),

]