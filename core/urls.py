from django.urls import path
from core.views import ProfileListView, FollowView,CreateUserView,PostCreateView,\
    PostListView,RecommendedPostView,ProfilePostView,ProfileDetailView,ProfilePhotoUploadView

urlpatterns = [
    path('profiles/', ProfileListView.as_view(), name='profile-list'),
    path('profiles/<int:pk>', ProfileDetailView.as_view(), name='profile-detail'),
    path('follow/<int:pk>', FollowView.as_view(), name='follow'),
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('profile-posts/<int:pk>/',ProfilePostView.as_view(), name = 'view-profile-posts'),
    path('profile/upload-photo', ProfilePhotoUploadView.as_view(), name='profile-upload-photo'),
    path('posts/list', PostListView.as_view(), name='posts-list'),
    path('posts/create', PostCreateView.as_view(), name='posts-create'),
    path('posts/recommended_posts', RecommendedPostView.as_view(), name='posts-recommeded-create')
]