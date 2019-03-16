import facebook
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday
from celery import shared_task


@shared_task
def publish_new_trip_on_fb(trip_id):
    from .models import Trip
    if settings.FACEBOOK_PAGE_ACCESS_TOKEN:
        graph = facebook.GraphAPI(
            access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN, version="3.1")
        trip = Trip.objects.get(id=trip_id)

        if trip.origin_address_components is None:
            return

        origin_city = trip.get_origin_adm_area_2()
        destination_city = trip.get_destination_adm_area_2()

        origin_state = trip.get_origin_adm_area_1(short=True)
        destination_state = trip.get_destination_adm_area_1(short=True)

        time = f"{naturalday(trip.datetime, 'd/m')} às {trip.datetime.strftime('%H:%M')}".capitalize()

        url = f"https://app.unicaronas.com/search/{trip.id}/"

        message = f"""[OFERECE]
{origin_city}, {origin_state} >> {destination_city}, {destination_state}
{time}
R${trip.price}, {trip.max_seats} vagas
Clique no link pra reservar 👇"""

        graph.put_object(
            parent_object="me",
            connection_name="feed",
            message=message,
            link=url)
