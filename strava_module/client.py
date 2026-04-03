import requests

from strava_module.auth import get_valid_token

from strava_module.settings import settings

class StravaClient:

    def __init__(self):
        token = get_valid_token()
        
        self.session = requests.Session()
        self.session.headers.update(
            {
                'Authorization' : f'Bearer {token}'
            }
        )

    def _request(self, method, endpoint, **kwargs):
        url = f"{settings.BASE_URL}/{endpoint}"
        response = self.session.request(
            method=method,
            url=url,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    

    # get athlete
    def get_athlete(self):
        return self._request("GET","athlete")
        
    
    # get activities
    def get_activities(self, page=1,per_page=200):
        params = {
            "page":page,
            "per_page":per_page
        }
        return self._request(
            "GET",
            "athlete/activities",
            params=params
        )
    
    # get activity based on given ID
    def get_activity(self, activity_id, include_all_efforts=False):
        params = {
            "include_all_efforts": str(include_all_efforts).lower()
        }
        return self._request(
            "GET",
            f"activities/{activity_id}",
            params=params
        )
        
    def get_gear(self, gear_id):
        return self._request(
            "GET",
            f"gear/{gear_id}"
        )

