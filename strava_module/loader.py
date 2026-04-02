from strava_module.client import StravaClient
import json
from pathlib import Path

client = StravaClient()

def fetch_activities_to_file(tmp_dir="/tmp", per_page=200):
    page =1 
    while True:
        activities = client.get_activities(page=page,per_page=per_page)
        
        if not activities:
            break
        
        file_path= Path(tmp_dir) / f"activities_page_{page}.json"
        
        with open (file_path,"w") as f:
            json.dump(activities, f)
     
        yield  file_path
        page+=1
        
def fetch_athlete(tmp_dir="/tmp"):
    athlete = client.get_athlete()

    file_path = Path(tmp_dir) / "athlete.json"

    with open(file_path, "w") as f:
        json.dump(athlete, f)

    yield file_path