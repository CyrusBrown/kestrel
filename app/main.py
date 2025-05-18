# The main file for the API
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from typing_extensions import Annotated

from .utils.database import Database

# Importing a router from its folder
from .database_functions import database_router
from .tba_functions import tba_router

# Importing the authentication function
from .utils.auth import check_key

# Load the environment variables from .env
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
    title="Kestrel",
    description="API for connecting to the 1678 scouting database",
    version="1.1.0",
    lifespan=db_lifespan # Include the database lifespan event
)

# Add the database router to the app
app.include_router(database_router.router,
                   tags=["Database"], 
                   prefix="/database", # Prefix every path in the router with /database
                   dependencies=[Depends(check_key)] # Every function in this router requires the api key 
                   )

app.include_router(database_router.unauthed_router,
                   tags=["Database"], 
                   prefix="/database"
                  )

app.include_router(tba_router.router,
                   tags=["TBA"],
                   prefix="/tba",
                   dependencies=[Depends(check_key)]
                   )


# The following is practically useless code for CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://frc1678.github.io",
    "https://script.googleusercontent.com",
    "https://script.google.com",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


