import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.artikel_dakwah_mq_controller import router as artikel_dakwah_mq_router
from controllers.program_and_adds_controller import router as program_and_adds_router
from controllers.audio_dakwah_streaming_controller import router as audio_dakwah_streaming_router
from controllers.youtube_dakwah_streaming_controller import router as youtube_dakwah_streaming_router
from controllers.audio_dakwah_mq_controller import router as audio_dakwah_mq_router
from controllers.otp_controller import router as otp_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="MQFM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artikel_dakwah_mq_router, prefix="/api")
app.include_router(program_and_adds_router, prefix="/api")
app.include_router(audio_dakwah_streaming_router, prefix="/api")
app.include_router(youtube_dakwah_streaming_router, prefix="/api")
app.include_router(audio_dakwah_mq_router, prefix="/api")
app.include_router(otp_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
