import logging
from generated import mqfm_pb2, mqfm_pb2_grpc
from audio_dakwah_streaming.infrastructure.cache_adapter import AudioDakwahStreamingCacheAdapter
from audio_dakwah_streaming.infrastructure.scraper_adapter import AudioDakwahStreamingScraperAdapter
from audio_dakwah_streaming.application.use_case import GetAudioDakwahStreamingUseCase

logger = logging.getLogger(__name__)


class AudioDakwahStreamingGrpcServicer(mqfm_pb2_grpc.AudioDakwahStreamingGrpcServicer):
    def GetAudioDakwahStreaming(self, request, context):
        cache = AudioDakwahStreamingCacheAdapter()
        scraper = AudioDakwahStreamingScraperAdapter()
        use_case = GetAudioDakwahStreamingUseCase(cache=cache, scraper=scraper)
        data = use_case.execute()

        return mqfm_pb2.AudioDakwahStreamingResponse(
            current_program=data.get("current_program") or "",
            schedule=data.get("schedule") or "",
            up_next_program=data.get("up_next_program") or "",
            up_next_schedule=data.get("up_next_schedule") or "",
            audio_url=data.get("audio_url") or "",
        )
