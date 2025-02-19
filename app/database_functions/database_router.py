from fastapi import APIRouter

from ..utils.database import Database

# Define the router object, all endpoints created from this
router = APIRouter()

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


@router.get("/{db_name}/obj_team")
async def get_obj_tim(db_name: str):
    db = Database.get_database(db_name)
    data = await db["obj_team"].find({}, {"_id": 0}).to_list(length=None)
    return data