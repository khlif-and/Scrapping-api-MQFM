import logging
from fastapi import FastAPI
from controllers.mqfm_controller import router as mqfm_router
from controllers.program_controller import router as program_router
from controllers.streaming_controller import router as streaming_router
from controllers.youtube_controller import router as youtube_router
from controllers.audio_controller import router as audio_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="MQFM API")

app.include_router(mqfm_router, prefix="/api")
app.include_router(program_router, prefix="/api")
app.include_router(streaming_router, prefix="/api")
app.include_router(youtube_router, prefix="/api")
app.include_router(audio_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
