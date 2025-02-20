from fastapi import APIRouter, HTTPException

from ..utils.database import Database
from pydantic import BaseModel

# Define the router object, all endpoints created from this
router = APIRouter()

VALID_TEAM_CATAGORIES = ["obj_team", "tba_team", "predicted_team", "pickability", "raw_obj_pit", "subj_team", "picklist"]
VALID_TIM_CATAGORIES = ["obj_tim", "tba_tim", "subj_tim"]

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
    if category not in VALID_TEAM_CATAGORIES:
        raise HTTPException(status_code=404, detail=f"Invalid team category: {category}")
    db = Database.get_database(event_key)
    data = await db[category].find({}, {"_id": 0}).to_list(length=None)

    team_data = {}
    for document in data:
        team_data[document["team_number"]] = document

    return team_data

@router.get("/tim/{event_key}/{category}")
async def get_obj_tim(event_key: str, category: str):
    if category not in VALID_TIM_CATAGORIES:
        raise HTTPException(status_code=404, detail=f"Invalid tim category: {category}")
    db = Database.get_database(event_key)
    data = await db[category].find({}, {"_id": 0}).to_list(length=None)

    obj_tim = {}
    for document in data:
        if document["match_number"] not in obj_tim:
            obj_tim[document["match_number"]] = {}
        obj_tim[document["match_number"]][document["team_number"]] = document

    return obj_tim

@router.get("/predicted_aim/{event_key}")
async def get_predicted_aim(event_key: str):
    db = Database.get_database(event_key)
    data = await db["predicted_aim"].find({}, {"_id": 0}).to_list(length=None)

    predicted_aim = {}
    for aim in data:
        if aim["match_number"] not in predicted_aim:
            predicted_aim[aim["match_number"]] = {"red": {}, "blue": {}}
        if aim["alliance_color_is_red"]:
            predicted_aim[aim["match_number"]]["red"] = aim
        else:
            predicted_aim[aim["match_number"]]["blue"] = aim

    return predicted_aim

@router.get("/auto_paths/{event_key}")
async def get_auto_paths(event_key: str):
    db = Database.get_database(event_key)
    data = await db["auto_paths"].find({}, {"_id": 0}).to_list(length=None)

    auto_paths = {}
    for path in data:
        if path["team_number"] not in auto_paths:
            auto_paths[path["team_number"]] = {}
        auto_paths[path["team_number"]][path["path_number"]] = path
    
    return auto_paths

@router.get("/ss_users/{event_key}")
async def get_ss_users(event_key: str):
    db = Database.get_database(event_key)
    data = await db["ss_team"].find({}, {"_id": 0}).to_list(length=None)

    ss_users = []
    for document in data:
        ss_users.append(document["username"])

    ss_users = list(set(ss_users))

    return ss_users

@router.get("/ss_team/{event_key}/{user}")
async def get_ss_team(event_key: str, user: str):
    db = Database.get_database(event_key)
    data = await db["ss_team"].find({"username": user}, {"_id": 0}).to_list(length=None)
    ss_team = {}
    for team in data:
        ss_team[team["team_num"]]
    return ss_team


@router.get("/ss_tim/{event_key}/{user}")
async def get_ss_team(event_key: str, user: str):
    db = Database.get_database(event_key)
    data = await db["ss_tim"].find({"username": user}, {"_id": 0}).to_list(length=None)
    ss_tim = {}
    for tim in data:
        if tim["match_number"] not in ss_tim:
            ss_tim[tim["match_number"]] = {}
        ss_tim[tim["match_number"]][tim["team_number"]] = tim
    return ss_tim

@router.get("/notes/{event_key}")
async def get_notes(event_key: str):
    db = Database.get_database(event_key)
    data = await db["notes"].find({}, {"_id": 0}).to_list(length=None)
    return {note["team_number"]: note for note in data}

class Note(BaseModel):
    note: str

@router.put("/notes/{event_key}/{team_num}")
async def add_new_note(event_key: str, team_num: str, note: Note):
    db = Database.get_database(event_key)
    result = await db["notes"].update_one({"team_number": team_num}, {"$set": {"note": note.note}}, upsert=True)
    return {"success": result.acknowledged}