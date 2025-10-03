import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, TheatreHall, Performance, Genre, Actor
from theatre.serializers import PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("theatre:play-list")  # /api/plays/
PERFORMANCE_URL = reverse("theatre:performance-list")  # /api/performances/


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
    """Test unauthenticated play API access."""

    def setUp(self):
        """Create a client and don't authenticate."""
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required."""
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    """Test authenticated play API access."""

    def setUp(self):
        """Create and authenticate a new user"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        """Test retrieving a list of plays."""
        sample_play()
        sample_play()

        res = self.client.get(PLAY_URL)

        plays = Play.objects.order_by("id")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_plays_by_genres(self):
        """Test retrieving plays by genre."""
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
        """Test retrieving plays by actor."""
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
        """Test retrieving plays by title."""
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

    def test_retrieve_play_detail(self):
        """Test retrieving a play detail"""
        play = sample_play()
        play.genres.add(Genre.objects.create(name="Genre"))
        play.actors.add(Actor.objects.create(
            first_name="Actor", last_name="Last")
        )
        url = detail_url(play.id)
        res = self.client.get(url)

        serializer = PlayDetailSerializer(play)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        """Test creating a play is forbidden for unauthorized user."""
        payload = {
            "title": "Test play",
            "description": "Test play description"
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTests(TestCase):
    def setUp(self) -> None:
        """Create and authenticate a new admin user."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        """Test creating a play is successful for the admin user."""
        payload = {
            "title": "Test play",
            "description": "Test play description"
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(play, key))

    def test_create_play_with_genres(self):
        """Test creating a play with genres is successful for the admin user"""
        genre1 = Genre.objects.create(name="Drama")
        genre2 = Genre.objects.create(name="Comedy")
        payload = {
            "title": "Test play",
            "description": "Test play description",
            "genres": [genre1.id, genre2.id]
        }
        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=res.data["id"])
        genres = play.genres.all()
        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_create_play_with_actors(self):
        """Test creating a play with actors is successful for the admin user"""
        actor1 = Actor.objects.create(first_name="Actor", last_name="Last")
        actor2 = Actor.objects.create(first_name="Actor2", last_name="Last2")
        payload = {
            "title": "Test play",
            "description": "Test play description",
            "actors": [actor1.id, actor2.id]
        }
        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=res.data["id"])
        actors = play.actors.all()
        self.assertEqual(actors.count(), 2)
        self.assertIn(actor1, actors)
        self.assertIn(actor2, actors)


class PlayImageUploadTests(TestCase):
    """Test the play image upload feature."""

    def setUp(self):
        """Create and authenticate a new admin user."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@superuser.com", "testpass"
        )
        self.client.force_authenticate(self.user)
        self.play = sample_play()
        self.performance = sample_performance(play=self.play)

    def tearDown(self):
        """Delete the play image file after each test."""
        self.play.image.delete()

    def test_upload_image_to_play(self):
        """Test uploading an image to play successfully."""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url, {"image": ntf}, format="multipart"
            )
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image fails."""
        url = image_upload_url(self.play.id)
        res = self.client.post(
            url, {"image": "notimage"}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_play_list_should_not_work(self):
        """Test uploading an image to play list should not work."""
        url = PLAY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Test play title",
                    "description": "Test play description",
                    "image": ntf
                },
                format="multipart"
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Test play title")
        self.assertFalse(play.image)

    def test_image_url_is_shown_on_play_detail(self):
        """Test that the image url is shown on the play detail view."""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.play.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_play_list(self):
        """Test that the image url is shown on the play list."""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PLAY_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_performance_detail(self):
        """Test that the image url is shown on the performance detail."""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PERFORMANCE_URL)

        self.assertIn("play_image", res.data[0].keys())

    def test_put_play_not_allowed(self):
        """Test that PUT requests are not allowed in play."""
        payload = {
            "title": "Test play",
            "description": "Test play description"
        }
        play = sample_play()
        url = detail_url(play.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_play_not_allowed(self):
        """Test that DELETE requests are not allowed in play."""
        play = sample_play()
        url = detail_url(play.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
