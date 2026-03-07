import logging
from generated import mqfm_pb2, mqfm_pb2_grpc
from audio_dakwah_mq.infrastructure.cache_adapter import AudioDakwahMqCacheAdapter
from audio_dakwah_mq.infrastructure.scraper_adapter import AudioDakwahMqScraperAdapter
from audio_dakwah_mq.application.use_case import GetAudioDakwahMqUseCase

logger = logging.getLogger(__name__)


class AudioDakwahMqGrpcServicer(mqfm_pb2_grpc.AudioDakwahMqGrpcServicer):
    def GetAudioDakwahMq(self, request, context):
        cache = AudioDakwahMqCacheAdapter()
        scraper = AudioDakwahMqScraperAdapter()
        use_case = GetAudioDakwahMqUseCase(cache=cache, scraper=scraper)
        data = use_case.execute()

        return mqfm_pb2.AudioDakwahMqResponse(
            programs=[
                mqfm_pb2.AudioProgram(
                    title=p["title"],
                    image_url=p["image_url"],
                    page_url=p["page_url"],
                    tracks=[
                        mqfm_pb2.AudioTrack(
                            title=t["title"],
                            mp3_url=t["mp3_url"],
                            duration=t.get("duration") or ""
                        )
                        for t in p["tracks"]
                    ],
                )
                for p in data["programs"]
            ]
        )
