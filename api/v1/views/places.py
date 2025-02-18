#!/usr/bin/python3
"""Place objects that handles all default RESTFul API actions"""

from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from flask import abort, request, jsonify


@app_views.route("/cities/<city_id>/places", strict_slashes=False,
                 methods=["GET"])
def places(city_id):
    """show places"""
    places_list = []
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = city.places
    for place in places:
        places_list.append(place.to_dict())
    return jsonify(places_list)


@app_views.route("/places/<place_id>", strict_slashes=False, methods=["GET"])
def get_place(place_id):
    """Retrieves a place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route("/places/<place_id>", strict_slashes=False,
                 methods=["DELETE"])
def place_delete(place_id):
    """delete method"""
    obj = storage.get(Place, place_id)
    if obj is None:
        abort(404)
    storage.delete(obj)
    storage.save()
    return jsonify({}), 200


@app_views.route("/cities/<city_id>/places", strict_slashes=False,
                 methods=["POST"])
def create_place(city_id):
    """create a new post req"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    data = request.get_json(force=True, silent=True)
    if not data:
        abort(400, "Not a JSON")
    if "user_id" not in data:
        abort(400, "Missing user_id")
    user = storage.get(User, data["user_id"])
    if user is None:
        abort(404)
    if "name" not in data:
        abort(400, "Missing name")
    new_place = Place(city_id=city.id, **data)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route("/places/<place_id>", strict_slashes=False, methods=["PUT"])
def update_placey(place_id):
    """update place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json(force=True, silent=True)
    if not data:
        abort(400, "Not a JSON")
    place.name = data.get("name", place.name)
    place.description = data.get("description",
                                 place.description)
    place.number_rooms = data.get("number_rooms",
                                  place.number_rooms)
    place.number_bathrooms = data.get("number_bathrooms",
                                      place.number_bathrooms)
    place.max_guest = data.get("max_guest", place.max_guest)
    place.price_by_night = data.get("price_by_night", place.price_by_night)
    place.latitude = data.get("latitude", place.latitude)
    place.longitude = data.get("longitude", place.longitude)
    place.save()
    return jsonify(place.to_dict()), 200

@app_views.route("/places_search", strict_slashes=False, methods=["POST"])
def places_search():
    """Search for Place objects based on JSON body"""
    # Check if the request body is valid JSON
    data = request.get_json(force=True, silent=True)
    if data is None:
        abort(400, "Not a JSON")

    # Initialize sets to store city IDs and place IDs
    city_ids = set()
    place_ids = set()

    # Retrieve all places if no criteria are provided
    if not data or all(len(lst) == 0 for lst in [data.get("states", []), data.get("cities", []), data.get("amenities", [])]):
        places = storage.all(Place).values()
        return jsonify([place.to_dict() for place in places])

    if "states" in data and data["states"]:
        for state_id in data["states"]:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    city_ids.add(city.id)

    if "cities" in data and data["cities"]:
        for city_id in data["cities"]:
            city_ids.add(city_id)

    for city_id in city_ids:
        city = storage.get(City, city_id)
        if city:
            for place in city.places:
                place_ids.add(place.id)

    if not city_ids:
        places = storage.all(Place).values()
    else:
        places = [storage.get(Place, place_id) for place_id in place_ids]

    if "amenities" in data and data["amenities"]:
        amenity_ids = set(data["amenities"])
        filtered_places = []
        for place in places:
            if place and all(amenity.id in [a.id for a in place.amenities] for amenity_id in amenity_ids):
                filtered_places.append(place)
        places = filtered_places

    return jsonify([place.to_dict() for place in places if place])
