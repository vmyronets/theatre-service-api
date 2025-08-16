from django.urls import path, include
from rest_framework import routers

from theatre.views import GenreViewSet, ActorViewSet, TheatreHallViewSet

router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("theatre_halls", TheatreHallViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "theatre"
