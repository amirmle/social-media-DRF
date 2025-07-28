from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', obtain_auth_token, name='auth_token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/followers/', views.FollowersView.as_view(), name='profile_follower'),
    path('profile/<slug:username>/following/', views.FollowingView.as_view(), name='profile_following'),
    path('profile/delete/', views.ProfileDeleteView.as_view(), name='profile_delete'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/post/', views.ProfilePostListView.as_view(), name='profile_post_list'),
    path('profile/post/<int:pk>/', views.ProfilePostDetailView.as_view(), name='profile_post_detail'),
    path('profile/<slug:username>/', views.ProfileOtherView.as_view(), name='profile_other'),
    path('profile/<slug:username>/follow/', views.FollowView.as_view(), name='follow'),

    path('profile/<slug:username>/post/', views.ProfileOtherPostListView.as_view(), name='profile_other_post_list'),


]