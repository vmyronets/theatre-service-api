from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, TheatreHall, Performance, Genre, Actor
from theatre.serializers import PlayListSerializer

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
        """Create a client and don't authenticate"""
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        """Create and authenticate a new user"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        """Test retrieving a list of plays"""
        sample_play()
        sample_play()

        res = self.client.get(PLAY_URL)

        plays = Play.objects.order_by("id")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_plays_by_genres(self):
        """Test retrieving plays by genre"""
        genre1 = Genre.objects.create(name="Genre 1")
        genre2 = Genre.objects.create(name="Genre 2")

        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        play3 = sample_play(title="Play without genres")

        res = self.client.get(
            PLAY_URL, {"genres": f"{genre1.id},{genre2.id}"}
        )
        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_actors(self):
        """Test retrieving plays by actor"""
        actor1 = Actor.objects.create(first_name="Actor 1", last_name="Last 1")
        actor2 = Actor.objects.create(first_name="Actor 2", last_name="Last 2")

        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        play3 = sample_play(title="Play without actors")

        res = self.client.get(
            PLAY_URL, {"actors": f"{actor1.id},{actor2.id}"}
        )
        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_title(self):
        """Test retrieving plays by title"""
        play1 = sample_play(title="Play")
        play2 = sample_play(title="Another Play")
        play3 = sample_play(title="No match")

        res = self.client.get(PLAY_URL, {"title": "play"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)