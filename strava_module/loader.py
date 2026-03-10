from client import StravaClient

client = StravaClient()

def load_activities():
    print(client.get_athlete())