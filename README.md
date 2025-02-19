# Kestrel


## Overview 

Kestrel is a part of FRC team 1678's scouting system. It connects various frontend devices to our backend database. It is a REST API, and built in python utilizing the fastapi library. Kestrel is designed to be as simple, understandable, and flexible as possible. It includes simple authentication and is designed to connect to a MongoDB database. Detailed documentation and much more is availiable on this repositorys wiki page
* Documentation 
* How to extend Kestrels functionailty 
* Deploying in production
* Common issues 


## Running Locally

If you're looking to run Kestrel locally, this guide will walk you through the steps.

### Virtual enviroment 
You'll first need to set up a virtual enviorment. The way I would recommend is the built in venv module in python. You can set up this method by running these commands in the terminal

* Create a new virtual enviroment: `python -m venv venv`

* Activate the enviorment: `source venv/bin/activate`

* Install the required packages: `pip install -r requirements.txt`


### Enviroment variables
In order to keep important data a secret, it is stored in enviroment variables. Copy the `env.example` file and rename it to `.env`.

 Inside you will find all the required enviroment variables, but without any values, so you will need to fill them in. 

* `MONGO_CONNECTION` This is the connection string for our cloud database, if you don't know where to find this, it's probably best to ask someone who does. It should include the full string, starting with the `mongodb+srv://`

* `API_KEY` This is the string that you need in order to access the API, because you are running locally you can put whatever you want.


### Starting the API server

To start the API server, there are a few ways. The way I would personally reccomend is to run `fastapi dev` in the terminal.   
It should start an api session and tell you where there server has been started, which should somthing look like `http://127.0.0.1:8000`.   
If you enter that into a browser, you won't see much. Instead go to the documentation page, found at your hosted link with `/docs` at the end, for example: `http://127.0.0.1:8000/docs`.  
Once you are at the docs, you will be able to test your various endpoints, but first you must authorize yourself. You can do this by just clicking the green button in the top right corner that says Authorize. Enter the api key you set in your enviorment variable and you should be good to go.

## Developing 

If you are here to contribute code, I would encourage you to take a look at the development sections of the wiki. If you're inexperiencied, there will be guides walking you through how kestrel functions. If you are experienced, I would still suggest looking there. There are suggestions on how to keep kestrel easy to maintain, run, and understand. 


### Why the name kestrel?
The previous 1678 API was named grosbeak, so I chose the name kestrel to continue the bird name scheme :)