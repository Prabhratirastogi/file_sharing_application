from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserSignupView, UserLoginView, FileUploadView, FileListView, FileDownloadView,
    EmailVerificationView,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/signup/', UserSignupView.as_view(), name='user-signup'),
    path('api/login/', UserLoginView.as_view(), name='user-login'),  # JWT login
    path('api/token/refresh/',TokenRefreshView.as_view(), name='token-refresh'),

    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/files/', FileListView.as_view(), name='file-list'),
    path('api/files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),

    path('api/email/verify/<str:token>/', EmailVerificationView.as_view(), name='email-verification'),
    path('api/files/download/<str:signed_url>/', FileDownloadView.as_view(), name='secure-file-download'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
