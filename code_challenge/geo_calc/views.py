import math
from decimal import Decimal, ROUND_DOWN
from typing import Union, List

import requests
from rest_framework import viewsets, status
from rest_framework.response import Response

from geo_calc.models import GoogleAddrWithCoord, SearchTerms
from code_challenge.settings import GOOGLE_MAP_API, API_KEY


class SearchLocationViewSet(viewsets.ModelViewSet):
    queryset = SearchTerms.objects.all()

    def get_location_from_search(self, search_text: str) -> Union[GoogleAddrWithCoord, None]:
        st = SearchTerms.objects.filter(search_term=search_text)
        if st.first():
            return GoogleAddrWithCoord.objects.get(id=st.first().coord_record.id)
        return None

    def haversine(self, loc_1: GoogleAddrWithCoord, loc_2: GoogleAddrWithCoord) -> Decimal:
        """
        Calculate distance between two points on sphere using decimal coords.
        :param loc_1:
        :param loc_2:
        :return:
        """

        r_earth = 6371000  # radius of Earth in meters
        lat1 = float(loc_1.coord_lat)
        lat2 = float(loc_2.coord_lat)
        lng1 = float(loc_1.coord_lng)
        lng2 = float(loc_2.coord_lng)

        phi_1 = math.radians(lat1)
        phi_2 = math.radians(lat2)

        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi_1) * math.cos(phi_2) * \
            math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # output distance in meters rounding down to the second decimal.
        return Decimal(r_earth * c).quantize(Decimal((0, (1,), -2)), rounding=ROUND_DOWN)

    def google_map_api_call(self, search_text: str) -> Union[List, Response]:

        response = requests.get(
            f"{GOOGLE_MAP_API}?address={search_text}&key={API_KEY}"
        )
        rstatus = response.json().get("status")
        if rstatus == 'ZERO_RESULTS':
            return Response(
                f"Google API responded with status: {rstatus} for the search string {search_text}. Check search terms and try again",
                status=status.HTTP_400_BAD_REQUEST
            )
        elif rstatus == 'REQUEST_DENIED':
            return Response(
                f"Google API responded with status: {rstatus}. Check .env for correct API key and try again.",
                status=status.HTTP_400_BAD_REQUEST
            )
        elif rstatus != 'OK':
            return Response(
                f"Google API responded with status: {rstatus}.",
                status=status.HTTP_400_BAD_REQUEST
            )

        return response.json().get("results")

    def list(self, request, *args, **kwargs):

        try:
            origin = request.data["origin_location"]
            destination = request.data["destination_location"]
        except KeyError as e:
            return Response(f"{e} is a required field", status=status.HTTP_400_BAD_REQUEST)

        final_data = {}
        coordinates = []
        formatted_address = ""
        for idx, loc in enumerate([origin, destination]):
            location_from_search = self.get_location_from_search(loc)
            if location_from_search:  # Don't use api if we've already got a record for the search term.
                coordinates.append(location_from_search)
                formatted_address = location_from_search.formatted_address
            else:  # create the new coord and search record
                search_term = loc.replace(" ", "+")
                results = self.google_map_api_call(search_term)
                if isinstance(results, Response):
                    return results
                elif results:
                    results = results[0]
                    lat = results["geometry"]["location"].get("lat")
                    lng = results["geometry"]["location"].get("lng")
                    formatted_address = results["formatted_address"]
                    coord = GoogleAddrWithCoord.objects.filter(formatted_address=formatted_address).first()
                    if not coord:
                        coord = GoogleAddrWithCoord(
                            coord_lat=lat,
                            coord_lng=lng,
                            formatted_address=formatted_address
                        )
                        coord.save()
                    coordinates.append(coord)
                    SearchTerms(
                        coord_record_id=coord.id,
                        search_term=loc
                    ).save()
            final_data[f"Location {idx+1}"] = formatted_address
        distance = self.haversine(coordinates[0], coordinates[1])
        final_data["Distance Between Locations"] = f"{str(distance)} meters"

        return Response(final_data, status=status.HTTP_200_OK)
