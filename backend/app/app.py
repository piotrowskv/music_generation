import asyncio
from pathlib import Path

from fastapi import (FastAPI, Form, HTTPException, UploadFile, WebSocket,
                     WebSocketDisconnect)
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


@app.websocket("/training/progress/{session_token}/ws")
async def training_progress(websocket: WebSocket, session_token: str) -> None:
    await websocket.accept()

    try:
        points = [
            m.ChartPoint(0, 1),
            m.ChartPoint(12, 3),
            m.ChartPoint(32, 5),
            m.ChartPoint(53, 10),
            m.ChartPoint(78, 11),
            m.ChartPoint(98, 14),
            m.ChartPoint(100, 16),
        ]

        for p in points[:-1]:
            await websocket.send_json(
                m.TrainingProgress(
                    finished=False,
                    y_label='Training progress [%]',
                    x_label='Time [s]',
                    chart_series=[
                        m.ChartSeries(
                            legend='Model 1',
                            points=[p])
                    ]).dict())
            await asyncio.sleep(2)

        await websocket.send_json(
            m.TrainingProgress(
                finished=True,
                y_label='Training progress [%]',
                x_label='Time [s]',
                chart_series=[
                    m.ChartSeries(
                        legend='Model 1',
                        points=[points[-1]])
                ]).dict())
    except WebSocketDisconnect:
        await websocket.close()
