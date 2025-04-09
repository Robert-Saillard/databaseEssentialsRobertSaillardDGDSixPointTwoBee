from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from bson import ObjectId
import motor.motor_asyncio

app = FastAPI()

# MongoDB connection setup
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://AdminIsTator:McastGaming@databaseassignment.3bdhqj5.mongodb.net/?retryWrites=true&w=majority&appName=DatabaseAssignment"
)
db = client.multimedia_db

# Pydantic model for player scores
class PlayerScore(BaseModel):
    player_name: str
    score: int

# Utility to convert MongoDB document ID to string
def serialize_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# ------------------ SPRITE ENDPOINTS ------------------

@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.get("/sprites")
async def get_all_sprites():
    sprites = await db.sprites.find().to_list(100)
    return [serialize_doc(sprite) for sprite in sprites]

@app.put("/sprite/{sprite_id}")
async def update_sprite(sprite_id: str, file: UploadFile = File(...)):
    content = await file.read()
    update_result = await db.sprites.update_one(
        {"_id": ObjectId(sprite_id)},
        {"$set": {"filename": file.filename, "content": content}}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite updated"}

@app.delete("/sprite/{sprite_id}")
async def delete_sprite(sprite_id: str):
    delete_result = await db.sprites.delete_one({"_id": ObjectId(sprite_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite deleted"}

# ------------------ AUDIO ENDPOINTS ------------------

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

@app.get("/audios")
async def get_all_audios():
    audios = await db.audio.find().to_list(100)
    return [serialize_doc(audio) for audio in audios]

@app.put("/audio/{audio_id}")
async def update_audio(audio_id: str, file: UploadFile = File(...)):
    content = await file.read()
    update_result = await db.audio.update_one(
        {"_id": ObjectId(audio_id)},
        {"$set": {"filename": file.filename, "content": content}}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return {"message": "Audio updated"}

@app.delete("/audio/{audio_id}")
async def delete_audio(audio_id: str):
    delete_result = await db.audio.delete_one({"_id": ObjectId(audio_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return {"message": "Audio deleted"}

# ------------------ PLAYER SCORE ENDPOINTS ------------------

@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

@app.get("/player_scores")
async def get_all_scores():
    scores = await db.scores.find().to_list(100)
    return [serialize_doc(score) for score in scores]

@app.put("/player_score/{score_id}")
async def update_score(score_id: str, score: PlayerScore):
    update_result = await db.scores.update_one(
        {"_id": ObjectId(score_id)},
        {"$set": score.dict()}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score updated"}

@app.delete("/player_score/{score_id}")
async def delete_score(score_id: str):
    delete_result = await db.scores.delete_one({"_id": ObjectId(score_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score deleted"}
