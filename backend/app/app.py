from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_database
from app.dto import models as m
from app.supported_models import SupportedModels

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

(training_sessions,) = create_database(Path('.'))


@app.get("/models", response_model=m.ModelVariants, description="Returns a list of all supported models")
def get_models() -> m.ModelVariants:
    models = [e.value for e in SupportedModels]

    return m.ModelVariants(models)


@app.post("/training/register", response_model=m.TrainingSessionCreated, description="Registers a new training session and returns the token for it")
async def register_training(files: list[UploadFile], model_id: str = Form()) -> m.TrainingSessionCreated:
    for file in files:
        if file.content_type != "audio/midi":
            raise HTTPException(
                status_code=400,
                detail="Uploaded files have to be of mimetype audio/midi")

    token = await training_sessions.register_session(model_id, files)

    return m.TrainingSessionCreated(token)
