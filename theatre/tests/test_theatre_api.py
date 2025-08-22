from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, TheatreHall, Performance

PLAY_URL = reverse("theatre:play-list")
PERFORMANCE_URL = reverse("theatre:performance-list")


def sample_play(**params):
    """Create and return a sample play"""
    defaults = {
        "title": "Sample play",
        "description": "Sample play description"
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_performance(**params):
    """Create and return a sample performance"""
    theatre_hall = TheatreHall.objects.create(
        name="Sample Theatre Hall",
        rows=15,
        seats_in_row=20
    )
    defaults = {
        "play": None,
        "theatre_hall": theatre_hall,
        "show_time": "2025-08-22 19:00:00"
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def image_upload_url(play_id):
    """Return URL for play image upload"""
    return reverse("theatre:play-upload-image", args=[play_id])


def detail_url(play_id):
    """Return play detail URL"""
    return reverse("theatre:play-detail", args=[play_id])


class UnauthenticatedPlayApiTests(TestCase):
    """Test unauthenticated play API access"""
    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

