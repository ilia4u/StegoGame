from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import json

app = FastAPI()

# Разрешаем CORS (чтобы WebGL мог отправлять запросы)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можешь заменить на свой домен
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Директории хранения
CHARACTERS_DIR = "characters"
LEVELS_DIR = "levels"
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(LEVELS_DIR, exist_ok=True)

# 📦 Модели данных
class PixelInfo(BaseModel):
    x: int
    y: int
    color: str

class PixelData(BaseModel):
    width: int
    height: int
    maskIndex: int
    pixels: List[PixelInfo]

class LevelEntry(BaseModel):
    index: int
    name: str
    data: PixelData

class LevelData(BaseModel):
    characters: List[LevelEntry]

# 🔹 CHARACTER ROUTES
@app.post("/character/save/{characterName}")
def save_character(characterName: str, data: PixelData):
    path = os.path.join(CHARACTERS_DIR, f"{characterName}.json")
    with open(path, "w") as f:
        json.dump(data.dict(), f)
    return {"status": "ok"}

@app.get("/character/list")
def list_characters():
    files = os.listdir(CHARACTERS_DIR)
    character_names = [f[:-5] for f in files if f.endswith(".json")]
    return {"characters": character_names}

@app.get("/character/{characterName}")
def load_character(characterName: str):
    path = os.path.join(CHARACTERS_DIR, f"{characterName}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Character not found")
    with open(path, "r") as f:
        data = json.load(f)
    return data

# 🔹 LEVEL ROUTES
@app.post("/level/save/{levelName}")
def save_level(levelName: str, level: LevelData):
    path = os.path.join(LEVELS_DIR, f"{levelName}.json")
    with open(path, "w") as f:
        json.dump(level.dict(), f)
    return {"status": "ok"}

@app.get("/level/list")
def list_levels():
    files = os.listdir(LEVELS_DIR)
    level_names = [f[:-5] for f in files if f.endswith(".json")]
    return {"levels": level_names}

@app.get("/level/{levelName}")
def load_level(levelName: str):
    path = os.path.join(LEVELS_DIR, f"{levelName}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Level not found")
    with open(path, "r") as f:
        data = json.load(f)
    return data

# 🔻 ПОСЛЕДНЕЕ! WebGL Build как статика
app.mount("/", StaticFiles(directory="Build", html=True), name="static")
