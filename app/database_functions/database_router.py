from fastapi import APIRouter, HTTPException, UploadFile
from bson import Binary
from fastapi.responses import Response

from ..utils.database import Database
from pydantic import BaseModel

# Define the router object, all endpoints created from this
router = APIRouter()
unauthed_router = APIRouter()

VALID_TEAM_CATEGORIES = ["obj_team", "tba_team", "predicted_team", "pickability", "predicted_alliances", "raw_obj_pit", "subj_team", "picklist", "ss_team"] # Define the valid team categories
VALID_TIM_CATEGORIES = ["obj_tim", "tba_tim", "subj_tim", "ss_tim"] # Define the valid tim categories
 
# Endpoint to test whether a given database exists and is working in the cluster
@router.get("/exists/{db_name}")
async def db_exists(db_name: str):

    db = Database.get_database(db_name) # Get the database
    ping = await db.command("ping") # Sends a ping to the database, returns a 1 or 0 in the ok field of the response

    return {"exists": ping["ok"]} # Return an exists field with a boolean value


@router.get("/db_list")
async def get_db_list():

    db_list = await Database.get_db_list()
    excluded_dbs = ["admin", "config", "local", "api", "__realm_sync", "static"]
    db_list = [db for db in db_list if db not in excluded_dbs] # Exclude the excluded databases

    return db_list

# Endpoint for getting all documents in a collection from a db
@router.get("/raw/{db_name}/{collection_name}")
async def get_collection(db_name: str, collection_name: str):

    db = Database.get_database(db_name) # get the database

    # Get all objects in the collection and exclude the _id field. Return as a list
    data = await db[collection_name].find({}, {"_id": 0}).to_list(length=None)

    return data

@router.put("/raw/{db_name}/{collection_name}")
async def add_new_document(db_name: str, collection_name: str, document: dict):
    
    db = Database.get_database(db_name)
    result = await db[collection_name].update_one({"team_number": document["team_number"]}, {"$set": document}, upsert=True)

    return {"success": result.acknowledged}

@router.get("/team/{event_key}/{category}")
async def get_obj_team(event_key: str, category: str):

    if category not in VALID_TEAM_CATEGORIES: # Make sure the category is valid
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

    if category not in VALID_TIM_CATEGORIES: # Make sure the category is valid
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
    tim = await db["ss_tim"].find({}, {"_id": 0}).to_list(length=None)
    team = await db["ss_team"].find({}, {"_id": 0}).to_list(length=None)
    data = tim + team

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
        ss_team[team["team_number"]] = team # Key each by team number
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
    if len(data) == 0:
        note = ""
    else:
        note = data[0]["notes"]
    return {"notes": note, "team_number": team_num} # Return the note and the team number

class Note(BaseModel):
    note: str

@router.put("/notes/{event_key}/{team_num}")
async def add_new_note(event_key: str, team_num: str, note: Note):
    db = Database.get_database(event_key)
    result = await db["notes"].update_one({"team_number": team_num},  # Update the note for the team number
                                          {"$set": {"notes": note.note}}, upsert=True)  # If the note doesn't exist, create it
    return {"success": result.acknowledged} # Return whether the operation was successful

@router.get("/scout_precision/{event_key}")
async def get_scout_precision(event_key: str):
    db = Database.get_database(event_key)

    # Get every document in the scout precision collection, removing the _id field
    data = await db["scout_precision"].find({}, {"_id": 0}).to_list(length=None)
    
    scout_precision_list = []

    # Loop through every scout precision document
    for document in data:

        # If the document has scout precision data, add the data to the list
        if "scout_precision" in document:
            scout_precision_list.append({
                "precision": document["scout_precision"],
                "rank": document["scout_precision_rank"],
                "name": document["scout_name"]
            })

    # Sort the scout precision by rank in ascending order
    return sorted(scout_precision_list, key=lambda d: d["rank"])


@router.put("/pit_collection/{event_key}")
async def add_new_pit_document(event_key: str, pit_data: dict):
    db = Database.get_database(event_key)
    
    successful_inserts = 0 
    
    # Loop through every new pit data document
    for doc in pit_data["pit_data"]:

        # If the document with the same team number is already in the database, update it with the new data. Otherwise create a new document
        result = await db["raw_obj_pit"].update_one({"team_number": doc["team_number"]}, {"$set": doc}, upsert=True)
        if result.acknowledged == "ok":
            successful_inserts += 1

    return {"successful_inserts": successful_inserts, "failed_inserts": len(pit_data) - successful_inserts}

@router.put("/pit_collection/images/{event_key}")
async def upload_pit_picture(event_key: str, picture: UploadFile):
    db = Database.get_database(event_key)

    collection = db["pit_images"]

    # Read the image file in binary mode
    image_data = await picture.read()

    # Wrap the image data using BSON Binary for safe storage in MongoDB
    binary_data = Binary(image_data)

    # Create a document that includes the filename and the image binary data
    document = {
        "filename": picture.filename,
        "image": binary_data
    }

    # Insert the document into the collection
    result = await collection.update_one({"filename": picture.filename}, {"$set": document}, upsert=True)

    return {"success": result.acknowledged, "filename": picture.filename}


@unauthed_router.get("/pit_collection/images/{event_key}/{image_name}")
async def get_pit_picture(event_key: str, image_name: str):
    db = Database.get_database(event_key)

    collection = db["pit_images"]

    # Retrieve the document by _id
    document = await collection.find_one({"filename": image_name}, {"_id": 0})
    
    if document is None:
        raise HTTPException(status_code=404, detail=f"Image {image_name} not found")
    
    # Get the binary image data from the document
    binary_data = document["image"]

    # Return the image data as a FileResponse
    return Response(content=binary_data, media_type="image/jpeg")

@router.delete("/pit_collection/images/{event_key}/{image_name}")
async def delete_pit_picture(event_key: str, image_name: str):
    db = Database.get_database(event_key)

    # Get the image collection
    collection = db["pit_images"]

    # Delete the document by filename
    result = await collection.delete_one({"filename": image_name})

    return {"success": result.acknowledged}

@unauthed_router.get("/pit_collection/image_list/{event_key}")
async def get_pit_image_list(event_key: str):
    db = Database.get_database(event_key)

    # Get every document in the pit images collection, without the _id or image, leaving just the name
    image_list = await db["pit_images"].find({}, {"_id": 0, "image": 0}).to_list(length=None)

    # Turn the list of dictionaries into just a list of strings
    image_names = [image["filename"] for image in image_list]

    return image_names
