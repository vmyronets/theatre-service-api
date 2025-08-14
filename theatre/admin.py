from django.contrib import admin


from theatre.models import (
    TheatreHall,
    Genre,
    Actor,
    Play,
    Performance,
    Order,
    Ticket
)

admin.site.register(TheatreHall)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Play)
admin.site.register(Performance)
admin.site.register(Order)
admin.site.register(Ticket)
