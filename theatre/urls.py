from rest_framework import routers

from theatre.views import GenreViewSet


router = routers.DefaultRouter()
router.register("genres", GenreViewSet)