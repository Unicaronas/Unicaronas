import facebook
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday
from celery import shared_task
import pytz


def build_post(trip):
    sp = pytz.timezone('America/Sao_Paulo')
    datetime = trip.datetime.astimezone(sp)
    origin_city = trip.get_origin_adm_area_2()
    destination_city = trip.get_destination_adm_area_2()

    origin_state = trip.get_origin_adm_area_1(short=True)
    destination_state = trip.get_destination_adm_area_1(short=True)

    origin_neighborhood = trip.get_origin_sublocality_level_1(short=True)
    destination_neighborhood = trip.get_destination_sublocality_level_1(short=True)

    origin_text = f"{origin_neighborhood}, {origin_city}" if origin_neighborhood else f"{origin_city}, {origin_state}"
    destination_text = f"{destination_neighborhood}, {destination_city}" if destination_neighborhood else f"{destination_city}, {destination_state}"

    time = f"{naturalday(datetime, 'd/m')} às {datetime.strftime('%H:%M')}".capitalize()

    url = f"https://app.unicaronas.com/search/{trip.id}/"
    message = f"""[OFERECE]
{origin_text} >> {destination_text}
{time}
R${trip.price}, {trip.max_seats} vagas
Clique no link pra reservar 👇"""
    return message, url


@shared_task
def publish_new_trip_on_fb(trip_id):
    from ..models import Trip
    if settings.FACEBOOK_PAGE_ACCESS_TOKEN:
        graph = facebook.GraphAPI(
            access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN, version="3.1")
        trip = Trip.objects.get(id=trip_id)

        if trip.origin_address_components is None:
            return

        message, url = build_post(trip)

        response = graph.put_object(
            parent_object="me",
            connection_name="feed",
            message=message,
            link=url)
        trip.facebook_post_id = response.get('id', '')
        trip.save()


@shared_task
def unpublish_trip_from_fb(post_id):
    if post_id and settings.FACEBOOK_PAGE_ACCESS_TOKEN:
        graph = facebook.GraphAPI(
            access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN, version="3.1")
        try:
            graph.delete_object(post_id)
        except facebook.GraphAPIError:
            pass
