from django.urls import include, path

urlpatterns = [
    path('v1/users/', include('apps.users.api.v1.urls', namespace='apps.users.api.v1'))
]
