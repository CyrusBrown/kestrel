# The main file for the API
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from typing_extensions import Annotated

# Non-module imports from the same directory must be prefixed with a dot
from .database import Database

# Importing a router from its folder
from .database_functions import database_router

# Importing the authentication function
from .auth import check_key 

# Load the enviroment variables from .env
load_dotenv()

# This defines a lifespan event, which runs code before and after the api starts
@asynccontextmanager
async def db_lifespan(app: FastAPI):

    # Before we start the api, we start the database connection.
    Database.initialize()

    yield

    # When the api stops, we close the connection
    Database.close_connection()

# Define the actual fastapi app
app = FastAPI(
    title="1678 Kestrel",
    description="API for connecting to the 1678 scouting database",
    version="1.0.0",
    lifespan=db_lifespan # Include the database lifespan event
)

# Add the database router to the app
app.include_router(database_router.router,
                   tags=["Database"], 
                   prefix="/database", # Prefix every path in the router with /database
                   dependencies=[Depends(check_key)] # Every function in this router requires the api key 
                   )


# The following is practically useless code for CORS, check the wiki for more information

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


