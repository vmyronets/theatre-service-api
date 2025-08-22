import os
import uuid

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TheatreHall(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name


def play_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/plays/", filename)


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="plays", blank=True)
    actors = models.ManyToManyField(Actor, related_name="plays", blank=True)
    image = models.ImageField(null=True, upload_to=play_image_file_path)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Performance(models.Model):
    play = models.ForeignKey(
        Play,
        on_delete=models.CASCADE,
        related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall,
        on_delete=models.CASCADE,
        related_name="performances"
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return f"{self.play.title} {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, theatre_hall, error_to_raise):
        """
        Checks if the specified row number and seats
        are within the valid range of the hall.
        Raises an error if the ticket is invalid.
        """
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            max_count = getattr(theatre_hall, theatre_hall_attr_name)
            if not (1 <= ticket_attr_value <= max_count):
                raise error_to_raise({
                    ticket_attr_name: (
                        f"{ticket_attr_name.capitalize()} must be between "
                        f"1 and {max_count}."
                    )
                })

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("performance", "row", "seat")
        ordering = ["row", "seat"]

    def __str__(self):
        return f"{self.performance} Row: {self.row}, Seat: {self.seat}"
