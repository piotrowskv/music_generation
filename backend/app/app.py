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


@app.post("/training/register", response_model=m.TrainingSessionCreated, description="Registers a new training session and returns the session ID for it")
async def register_training(files: list[UploadFile], model_id: str = Form()) -> m.TrainingSessionCreated:
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one training file has to be uploaded")

    for file in files:
        if file.content_type != "audio/midi":
            raise HTTPException(
                status_code=400,
                detail="Uploaded files have to be of mimetype audio/midi")

    session_id = await training_sessions.register_session(model_id, files)

    return m.TrainingSessionCreated(session_id)


@app.get("/training/{session_id}", response_model=m.TrainingSession, description="Returns information about a training session")
async def get_training_session(session_id: str) -> m.TrainingSession:
    session = await training_sessions.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"No session with id {session_id} found")

    model = SupportedModels.from_model_id(session.model_id)
    if model is None:
        raise HTTPException(
            status_code=410,
            detail=f"This session is connected to a no longer supported model")

    return m.TrainingSession(
        session_id,
        model.value,
        session.created_at,
        session.training_file_names)


@app.websocket("/training/{session_id}/progress/ws")
async def training_progress(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()

    try:
        points = [
            m.ChartPoint(1, 0),
            m.ChartPoint(3, 12),
            m.ChartPoint(5, 32),
            m.ChartPoint(10, 53),
            m.ChartPoint(11, 78),
            m.ChartPoint(14, 98),
            m.ChartPoint(16, 100),
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
