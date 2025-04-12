from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from bson import ObjectId
import motor.motor_asyncio
import re


app = FastAPI()

with open("password.txt", "r") as f:
    line = f.readline()  # Read the first line from the password file
    username, password = line.strip().split(":")
    
    # MongoDB connection setup using Motor (async MongoDB driver)
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb+srv://{username}:{password}@databaseassignment.3bdhqj5.mongodb.net/?retryWrites=true&w=majority&appName=DatabaseAssignment"
    )

db = client.multimedia_db  # Database reference

class PlayerScore(BaseModel):  # Pydantic model for validating player score input
    player_name: str
    score: int

# Utility to convert MongoDB document ID to string and remove internal _id field
def serialize_doc(doc):
    doc["id"] = str(doc["_id"])  # Convert ObjectId to string for JSON compatibility
    del doc["_id"]  # Remove MongoDB internal _id to avoid duplication
    return doc

# ------------------ SPRITE ENDPOINTS ------------------

@app.post("/upload_sprite")  # Endpoint to upload sprite image
async def upload_sprite(file: UploadFile = File(...)):
    '''
    Upload a sprite image file.
    The file is stored in the database with its filename and binary content.
    '''
    content = await file.read()  # Read binary content of uploaded file
    
    # Validate file content and type
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if not file.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    sprite_doc = {"filename": file.filename, "content": content}  # Construct document
    result = await db.sprites.insert_one(sprite_doc)  # Insert into 'sprites' collection
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}  # Return confirmation and ID

@app.get("/sprites")  # Endpoint to fetch all sprites' metadata
async def get_all_sprites():
    '''
    Retrieve all sprite images from the database.
    Returns a list of metadata for each sprite.
    '''
    sprites = await db.sprites.find().to_list(None)  # Fetch all sprite documents
    return [
        {
            "id": str(sprite["_id"]),  # Convert ObjectId to string
            "filename": sprite["filename"],  # Include filename
            "content": sprite["content"].hex()  # Convert binary to hex string for JSON safety
        }
        for sprite in sprites
    ]

@app.get("/sprite/{sprite_id}")  # Endpoint to retrieve a specific sprite by ID
async def get_sprite(sprite_id: str):
    '''
    Retrieve a specific sprite image by its ID.
    Returns the sprite's filename and binary content.
    '''
    sprite = await db.sprites.find_one({"_id": ObjectId(sprite_id)})  # Query by ObjectId
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")  # Error if not found
    return {
        "id": str(sprite["_id"]),
        "filename": sprite["filename"],
        "content": sprite["content"].hex()
    }

@app.put("/sprite/{sprite_id}")  # Endpoint to update a sprite's image file
async def update_sprite(sprite_id: str, file: UploadFile = File(...)):
    '''
    Update a sprite image file by its ID.
    The new file replaces the existing one in the database.
    '''
    content = await file.read()  # Read new binary content

    # Validate file content and type
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if not file.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type")

    update_result = await db.sprites.update_one(
        {"_id": ObjectId(sprite_id)},  # Match by ObjectId
        {"$set": {"filename": file.filename, "content": content}}  # Replace with new data
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite updated"}  # Confirm update

@app.delete("/sprite/{sprite_id}")  # Endpoint to delete a sprite by ID
async def delete_sprite(sprite_id: str):
    '''
    Delete a sprite image file by its ID.
    Removes the sprite from the database.
    '''
    delete_result = await db.sprites.delete_one({"_id": ObjectId(sprite_id)})  # Delete by ObjectId
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite deleted"}  # Confirm deletion

# ------------------ AUDIO ENDPOINTS ------------------

@app.post("/upload_audio")  # Endpoint to upload an audio file
async def upload_audio(file: UploadFile = File(...)):
    '''
    Upload an audio file.
    The file is stored in the database with its filename and binary content.
    '''
    content = await file.read()  # Read binary data

    # Validate file content and type
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if not file.filename.endswith(('.mp3', '.wav', '.ogg')):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    audio_doc = {"filename": file.filename, "content": content}  # Create document
    result = await db.audio.insert_one(audio_doc)  # Insert into 'audio' collection
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

@app.get("/audios")  # Endpoint to get metadata for all audio files
async def get_all_audios():
    '''
    Retrieve all audio files from the database.
    Returns a list of metadata for each audio file.
    '''
    audios = await db.audio.find().to_list(None)  # Fetch all audio documents
    return [
        {
            "id": str(audio["_id"]),
            "filename": audio["filename"],
            "content": audio["content"].hex()  # Convert binary to hex
        }
        for audio in audios
    ]

@app.get("/audio/{audio_id}")  # Endpoint to get a specific audio file by ID
async def get_audio(audio_id: str):
    '''
    Retrieve a specific audio file by its ID.
    '''
    audio = await db.audio.find_one({"_id": ObjectId(audio_id)})  # Find audio by ObjectId
    if not audio:
        raise HTTPException(status_code=404, detail="Audio file not found")

    return {
        "id": str(audio["_id"]),
        "filename": audio["filename"],
        "content": audio["content"].hex()
    }

@app.put("/audio/{audio_id}")  # Endpoint to update audio file by ID
async def update_audio(audio_id: str, file: UploadFile = File(...)):
    '''
    Update an audio file by its ID.
    The new file replaces the existing one in the database.
    '''
    content = await file.read()

    # Validate file content and type
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if not file.filename.endswith(('.mp3', '.wav', '.ogg')):
        raise HTTPException(status_code=400, detail="Invalid file type")

    update_result = await db.audio.update_one(
        {"_id": ObjectId(audio_id)},
        {"$set": {"filename": file.filename, "content": content}}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return {"message": "Audio updated"}

@app.delete("/audio/{audio_id}")  # Endpoint to delete an audio file by ID
async def delete_audio(audio_id: str):
    '''
    Delete an audio file by its ID.
    Removes the audio from the database.
    '''
    delete_result = await db.audio.delete_one({"_id": ObjectId(audio_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return {"message": "Audio deleted"}

# ------------------ PLAYER SCORE ENDPOINTS ------------------

@app.post("/upload_player_score")  # Endpoint to add a new player score
async def add_score(score: PlayerScore):
    '''
    Add a new player score to the database.
    The score includes the player's name and their score.
    '''
    score_doc = score.dict()  # Convert Pydantic model to dictionary

    # Validate score value
    if not score_doc["player_name"]:
        raise HTTPException(status_code=400, detail="Player name is required")
    if not isinstance(score_doc["score"], int):
        raise HTTPException(status_code=400, detail="Score must be an integer")
    if score_doc["score"] < 0:
        raise HTTPException(status_code=400, detail="Score must be non-negative")

    #Cleanup player name to remove special characters
    score_doc["player_name"] = re.sub(r'[^a-zA-Z0-9 ]', '', score_doc["player_name"])

    result = await db.scores.insert_one(score_doc)  # Insert into 'scores' collection
    return {"message": "Score recorded", "id": str(result.inserted_id)}

@app.get("/player_scores")  # Endpoint to retrieve all player scores
async def get_all_scores():
    '''
    Retrieve all player scores from the database.
    Returns a list of scores with player names and their scores.
    '''
    scores = await db.scores.find().to_list(None)  # Get all score documents
    return [serialize_doc(score) for score in scores]  # Convert each for safe JSON return

@app.get("/player_score/{score_id}")  # Endpoint to get a specific score by ID
async def get_score(score_id: str):
    '''
    Retrieve a specific player score by its ID.
    '''

    score = await db.scores.find_one({"_id": ObjectId(score_id)})  # Query by ObjectId
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return serialize_doc(score)

@app.put("/player_score/{score_id}")  # Endpoint to update a score by ID
async def update_score(score_id: str, score: PlayerScore):
    '''
    Update a player score by its ID.
    The new score replaces the existing one in the database.
    '''
    
    # Validate score value
    if not score.player_name:
        raise HTTPException(status_code=400, detail="Player name is required")
    if not isinstance(score.score, int):
        raise HTTPException(status_code=400, detail="Score must be an integer")
    if score.score < 0:
        raise HTTPException(status_code=400, detail="Score must be non-negative")
    
    score_dict = score.dict()  # Convert Pydantic model to dictionary

    #Cleanup player name to remove special characters
    score_dict["player_name"] = re.sub(r'[^a-zA-Z0-9 ]', '', score_dict["player_name"])

    update_result = await db.scores.update_one(
        {"_id": ObjectId(score_id)},  # Match score by ID
        {"$set": score_dict}  # Apply updated score data
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return {"message": "Score updated"}

@app.delete("/player_score/{score_id}")  # Endpoint to delete a score by ID
async def delete_score(score_id: str):
    '''
    Delete a player score by its ID.
    Removes the score from the database.
    '''
    delete_result = await db.scores.delete_one({"_id": ObjectId(score_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score deleted"}