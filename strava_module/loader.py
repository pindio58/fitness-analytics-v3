from strava_module.client import StravaClient

client = StravaClient()

def load_activities():
    page =1 
    while True:
        activities = client.get_activities()
        if not activities:
            break
        print(activities)

        page+=1