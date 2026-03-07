import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from artikel_dakwah_mq.infrastructure.rest_adapter import router as artikel_dakwah_mq_router
from audio_dakwah_mq.infrastructure.rest_adapter import router as audio_dakwah_mq_router
from audio_dakwah_streaming.infrastructure.rest_adapter import router as audio_dakwah_streaming_router
from youtube_dakwah_streaming.infrastructure.rest_adapter import router as youtube_dakwah_streaming_router
from program_and_adds.infrastructure.rest_adapter import router as program_and_adds_router
from otp.infrastructure.rest_adapter import router as otp_router

from generated import mqfm_pb2_grpc
from shared.grpc_server import create_grpc_server, start_grpc_server
from shared.scheduler import warm_cache, start_scheduler

from artikel_dakwah_mq.infrastructure.grpc_adapter import ArtikelDakwahMqGrpcServicer
from audio_dakwah_mq.infrastructure.grpc_adapter import AudioDakwahMqGrpcServicer
from audio_dakwah_streaming.infrastructure.grpc_adapter import AudioDakwahStreamingGrpcServicer
from youtube_dakwah_streaming.infrastructure.grpc_adapter import YoutubeDakwahStreamingGrpcServicer
from program_and_adds.infrastructure.grpc_adapter import ProgramAndAddsGrpcServicer
from otp.infrastructure.grpc_adapter import OTPGrpcServicer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_grpc_server():
    server, port = create_grpc_server(port=50051)
    mqfm_pb2_grpc.add_ArtikelDakwahMqGrpcServicer_to_server(ArtikelDakwahMqGrpcServicer(), server)
    mqfm_pb2_grpc.add_AudioDakwahMqGrpcServicer_to_server(AudioDakwahMqGrpcServicer(), server)
    mqfm_pb2_grpc.add_AudioDakwahStreamingGrpcServicer_to_server(AudioDakwahStreamingGrpcServicer(), server)
    mqfm_pb2_grpc.add_YoutubeDakwahStreamingGrpcServicer_to_server(YoutubeDakwahStreamingGrpcServicer(), server)
    mqfm_pb2_grpc.add_ProgramAndAddsGrpcServicer_to_server(ProgramAndAddsGrpcServicer(), server)
    mqfm_pb2_grpc.add_OTPGrpcServicer_to_server(OTPGrpcServicer(), server)
    start_grpc_server(server, port)
    server.wait_for_termination()


@asynccontextmanager
async def lifespan(application: FastAPI):
    grpc_thread = threading.Thread(target=run_grpc_server, daemon=True)
    grpc_thread.start()
    logger.info("gRPC server started on port 50051")

    cache_thread = threading.Thread(target=warm_cache, daemon=True)
    cache_thread.start()

    scheduler = start_scheduler()

    yield

    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


app = FastAPI(title="MQFM API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artikel_dakwah_mq_router, prefix="/api")
app.include_router(audio_dakwah_mq_router, prefix="/api")
app.include_router(audio_dakwah_streaming_router, prefix="/api")
app.include_router(youtube_dakwah_streaming_router, prefix="/api")
app.include_router(program_and_adds_router, prefix="/api")
app.include_router(otp_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
