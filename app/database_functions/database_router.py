from fastapi import APIRouter, HTTPException

from ..utils.database import Database
from pydantic import BaseModel

# Define the router object, all endpoints created from this
router = APIRouter()

VALID_TEAM_CATAGORIES = ["obj_team", "tba_team", "predicted_team", "pickability", "raw_obj_pit", "subj_team", "picklist"] # Define the valid team categories
VALID_TIM_CATAGORIES = ["obj_tim", "tba_tim", "subj_tim"] # Define the valid tim categories
 
# Endpoint to test whether a given database exists and is working in the cluster
@router.get("/exists/{db_name}")
async def db_exists(db_name: str):

    db = Database.get_database(db_name) # Get the database
    ping = await db.command("ping") # Sends a ping to the database, returns a 1 or 0 in the ok field of the response

    return {"exists": ping["ok"]} # Return an exists field with a boolean value



# Endpoint for getting all documents in a collection from a db
@router.get("/raw/{db_name}/{collection_name}")
async def get_collection(db_name: str, collection_name: str):

    db = Database.get_database(db_name) # get the database

    # Get all objects in the collection and exclude the _id field. Return as a list
    data = await db[collection_name].find({}, {"_id": 0}).to_list(length=None)

    return data


@router.get("/team/{event_key}/{category}")
async def get_obj_team(event_key: str, category: str):

    if category not in VALID_TEAM_CATAGORIES: # Make sure the category is valid
        raise HTTPException(status_code=404, detail=f"Invalid team category: {category}")
    
    db = Database.get_database(event_key) # Get the database
    data = await db[category].find({}, {"_id": 0}).to_list(length=None) # Get all documents in the collection without the _id field

    team_data = {}
    for document in data:
        # Viewer wants us to send datapoints with a list value as a string
        for datapoint in document.keys():
            if "mode" in datapoint:
                document[datapoint] = str(document[datapoint])
        team_data[document["team_number"]] = document # Create a dictionary with the team number as the key and the document as the value

    return team_data

@router.get("/tim/{event_key}/{category}")
async def get_obj_tim(event_key: str, category: str):

    if category not in VALID_TIM_CATAGORIES: # Make sure the category is valid
        raise HTTPException(status_code=404, detail=f"Invalid tim category: {category}")
    
    db = Database.get_database(event_key)
    data = await db[category].find({}, {"_id": 0}).to_list(length=None)

    obj_tim = {}
    for document in data:
        if document["match_number"] not in obj_tim: # If the match number is not in the dictionary, add it
            obj_tim[document["match_number"]] = {}
        obj_tim[document["match_number"]][document["team_number"]] = document # Add the team to the match

    return obj_tim

@router.get("/predicted_aim/{event_key}")
async def get_predicted_aim(event_key: str):
    db = Database.get_database(event_key)
    data = await db["predicted_aim"].find({}, {"_id": 0}).to_list(length=None)

    predicted_aim = {}
    for aim in data:
        if aim["match_number"] not in predicted_aim: # If the match number is not in the dictionary, add it
            predicted_aim[aim["match_number"]] = {"red": {}, "blue": {}} # initialize it with empty dictionaries for the red and blue
        aim["team_numbers"] = str(aim["team_numbers"]) # Viewer wants team numbers as a str representation of the list
        if aim["alliance_color_is_red"]: 
            predicted_aim[aim["match_number"]]["red"] = aim # Add the aim to the red alliance
        else:
            predicted_aim[aim["match_number"]]["blue"] = aim # Add the aim to the blue alliance

    return predicted_aim

@router.get("/auto_paths/{event_key}")
async def get_auto_paths(event_key: str):
    db = Database.get_database(event_key)
    data = await db["auto_paths"].find({}, {"_id": 0}).to_list(length=None)

    auto_paths = {}
    for path in data:
        if path["team_number"] not in auto_paths: # If the team number is not in the dictionary, add it
            auto_paths[path["team_number"]] = {}
        path["match_numbers_played"] = str(path["match_numbers_played"])
        auto_paths[path["team_number"]][path["path_number"]] = path # Add the path to the team
    
    return auto_paths

@router.get("/ss_users/{event_key}")
async def get_ss_users(event_key: str):
    db = Database.get_database(event_key)
    data = await db["ss_team"].find({}, {"_id": 0}).to_list(length=None)

    ss_users = []
    for document in data:
        ss_users.append(document["username"]) # Add the username to the list of users

    ss_users = list(set(ss_users)) # Remove duplicates

    return ss_users

@router.get("/ss_team/{event_key}/{user}")
async def get_ss_team(event_key: str, user: str):
    db = Database.get_database(event_key)
    data = await db["ss_team"].find({"username": user}, {"_id": 0}).to_list(length=None)
    ss_team = {}
    for team in data:
        ss_team[team["team_num"]] # Key each by team number
    return ss_team


@router.get("/ss_tim/{event_key}/{user}")
async def get_ss_team(event_key: str, user: str):
    db = Database.get_database(event_key)
    data = await db["ss_tim"].find({"username": user}, {"_id": 0}).to_list(length=None)
    ss_tim = {}
    for tim in data:
        if tim["match_number"] not in ss_tim:
            ss_tim[tim["match_number"]] = {} # Create empty dictionary for the match number
        ss_tim[tim["match_number"]][tim["team_number"]] = tim # Add the team to the match keyed by team number
    return ss_tim

@router.get("/notes/{event_key}")
async def get_notes(event_key: str):
    db = Database.get_database(event_key)
    data = await db["notes"].find({}, {"_id": 0}).to_list(length=None)
    return {note["team_number"]: note["notes"] for note in data} # Key each note by team number

@router.get("/notes/{event_key}/{team_num}")
async def get_notes(event_key: str, team_num: str):
    db = Database.get_database(event_key)
    data = await db["notes"].find({"team_number": team_num}, {"_id": 0}).to_list(length=None)
    return {"notes": data["notes"], "team_number": team_num} # Return the note and the team number

class Note(BaseModel):
    note: str

@router.put("/notes/{event_key}/{team_num}")
async def add_new_note(event_key: str, team_num: str, note: Note):
    db = Database.get_database(event_key)
    result = await db["notes"].update_one({"team_number": team_num},  # Update the note for the team number
                                          {"$set": {"note": note.note}}, upsert=True)  # If the note doesn't exist, create it
    return {"success": result.acknowledged} # Return whether the operation was successful

@router.get("/scout_precision/{event_key}")
async def get_scout_precision(event_key: str):
    db = Database.get_database(event_key)
    data = await db["scout_precision"].find({}, {"_id": 0}).to_list(length=None)

    
    scout_precision = {}
    for document in data:
        if "scout_precision" in document:
            scout_precision[document["scout_name"]] = {"precision": document["scout_precision"], "rank": document["scout_precision_rank"]}

    return scout_precision