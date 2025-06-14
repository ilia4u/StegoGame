from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os, json

app = FastAPI()

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ограничь на проде
    allow_methods=["*"],
    allow_headers=["*"],
)

# Отдаём WebGL билд как статику
app.mount("/", StaticFiles(directory="Build", html=True), name="static")

# Директории
CHARACTERS_DIR = "characters"
LEVELS_DIR = "levels"
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(LEVELS_DIR, exist_ok=True)

# Модели
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

# Эндпоинты
@app.post("/character/save/{characterName}")
def save_character(characterName: str, data: PixelData):
    path = os.path.join(CHARACTERS_DIR, f"{characterName}.json")
    with open(path, "w") as f:
        json.dump(data.dict(), f)
    return {"status": "ok"}

@app.get("/character/list")
def list_characters():
    files = os.listdir(CHARACTERS_DIR)
    return {"characters": [f[:-5] for f in files if f.endswith(".json")]}

@app.get("/character/{characterName}")
def load_character(characterName: str):
    path = os.path.join(CHARACTERS_DIR, f"{characterName}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    with open(path) as f:
        return json.load(f)

@app.post("/level/save/{levelName}")
def save_level(levelName: str, level: LevelData):
    path = os.path.join(LEVELS_DIR, f"{levelName}.json")
    with open(path, "w") as f:
        json.dump(level.dict(), f)
    return {"status": "ok"}

@app.get("/level/list")
def list_levels():
    files = os.listdir(LEVELS_DIR)
    return {"levels": [f[:-5] for f in files if f.endswith(".json")]}

@app.get("/level/{levelName}")
def load_level(levelName: str):
    path = os.path.join(LEVELS_DIR, f"{levelName}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    with open(path) as f:
        return json.load(f)
