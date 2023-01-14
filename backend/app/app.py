from pathlib import Path

from fastapi import (BackgroundTasks, FastAPI, Form, Header, HTTPException,
                     UploadFile, WebSocket, WebSocketDisconnect)
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_database
from app.dto import models as m
from app.dto.error import EndpointError
from app.supported_models import SupportedModels
from app.training_manager import TrainingManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


(training_sessions, training_progress) = create_database(Path('.'))
training_manager = TrainingManager(training_progress)


@app.get("/models",
         response_model=m.ModelVariants,
         description="Returns a list of all supported models")
def get_models() -> m.ModelVariants:
    models = [e.value for e in SupportedModels]

    return m.ModelVariants(models)


@app.post("/training/register",
          response_model=m.TrainingSessionCreated,
          description="Registers a new training session and returns the session ID for it",
          responses={
              400: {"description": "No training files passed", "model": EndpointError},
              410: {"description": "Model is no longer supported", "model": EndpointError},
              413: {"description": "Uploaded files are too large", "model": EndpointError},
              415: {"description": "Incorrect mimetype of uploaded files", "model": EndpointError},
              500: {"description": "Failed to create training session", "model": EndpointError},
          })
async def register_training(background_tasks: BackgroundTasks, files: list[UploadFile], model_id: str = Form(), content_length: int = Header()) -> m.TrainingSessionCreated:
    if content_length > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Uploaded MIDI files can be at most 10MB")

    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one training file has to be uploaded")

    for file in files:
        if file.content_type != "audio/midi":
            raise HTTPException(
                status_code=415,
                detail="Uploaded files have to be of mimetype audio/midi")

    model = SupportedModels.from_model_id(model_id)
    if model is None:
        raise HTTPException(
            status_code=410,
            detail=f"Model with an ID {model_id} is not supported")

    session_id = await training_sessions.register_session(model_id, files)

    training_data = await training_sessions.get_training_data(session_id)
    if training_data is None:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve newly created training data")

    background_tasks.add_task(
        training_manager.add_model, session_id, model.get_model(), training_data.midi)

    return m.TrainingSessionCreated(session_id)


@app.get("/training/{session_id}",
         response_model=m.TrainingSession,
         description="Returns information about a training session",
         responses={
             404: {"description": "Session does not exist", "model": EndpointError},
             410: {"description": "Session used a no longer supported model", "model": EndpointError},
         })
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


@app.get("/training",
         response_model=m.AllTrainingSessions,
         description="Returns all existing training sessions, except those that used a no longer supported model.")
async def get_training_sessions() -> m.AllTrainingSessions:
    sessions = await training_sessions.get_all_sessions()

    mapped_sessions: list[m.TrainingSessionSummary] = []

    for s in sessions:
        model = SupportedModels.from_model_id(s.model_id)
        if model is None:
            # ignore no longer supported models
            continue
        mapped_sessions.append(
            m.TrainingSessionSummary(
                session_id=s.session_id,
                created_at=s.created_at,
                file_count=s.file_count,
                model_name=model.name,
                training_completed=s.training_completed))

    return m.AllTrainingSessions(mapped_sessions)


@app.websocket("/training/{session_id}/progress/ws")
async def get_training_progress(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()

    training_data = await training_sessions.get_training_data(session_id)
    if training_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session with id {session_id} not found")

    model = SupportedModels.from_model_id(training_data.model_id)
    if model is None:
        raise HTTPException(
            status_code=400,
            detail=f"Model with an ID {training_data.model_id} is not supported")

    meta = model.get_model_type().get_progress_metadata()

    try:
        await websocket.send_json(
            m.TrainingProgress(
                finished=False,
                x_label=meta.x_label,
                y_label=meta.y_label,
                legends=meta.legends,
                chart_series_points=[]).dict())

        async for points in training_progress.subscribe(session_id):
            await websocket.send_json(
                m.TrainingProgress(
                    finished=False,
                    x_label=meta.x_label,
                    y_label=meta.y_label,
                    legends=meta.legends,
                    chart_series_points=[
                        [m.ChartPoint(x, y) for (x, y) in series] for series in points
                    ]).dict())

        await websocket.send_json(
            m.TrainingProgress(
                finished=True,
                x_label=meta.x_label,
                y_label=meta.y_label,
                legends=meta.legends,
                chart_series_points=[]).dict())

    except WebSocketDisconnect:
        await websocket.close()
