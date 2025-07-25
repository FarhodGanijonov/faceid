from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserPasswordChangeView, UploadPassportAPIView, \
    CompareFaceAPIView, ViewPassportImageAPIView, ViewFaceImageAPIView
from .views import (
    UpdateContactView,
    ProfileUpdateView,
    UserInfoView,
    LogoutView,
    ProfileImageDeleteView,
    GlobalContactView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('change-password/', UserPasswordChangeView.as_view(), name='user-change-password'),
    path('upload-passport/', UploadPassportAPIView.as_view(), name='upload-passport'),
    path('upload-face/', CompareFaceAPIView.as_view(), name='compare-face'),


    path('profile/contact/update/', UpdateContactView.as_view(), name='contact-update'),       # POST
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),               # PATCH
    path('profile/info/', UserInfoView.as_view(), name='profile-info'),                        # GET
    path('profile/logout/', LogoutView.as_view(), name='logout'),
    path('profile/image/', ProfileImageDeleteView.as_view(), name='profile-image-delete'),
    path('user/profile/me/', GlobalContactView.as_view()),

    path('view-passport-image/', ViewPassportImageAPIView.as_view(), name='view-passport-image'),
    path('view-face-image/', ViewFaceImageAPIView.as_view(), name='view-face-image'),

]

