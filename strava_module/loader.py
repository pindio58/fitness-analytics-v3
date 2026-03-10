from strava_module.client import StravaClient

client = StravaClient()

def load_activities():
    print(client.get_athlete())