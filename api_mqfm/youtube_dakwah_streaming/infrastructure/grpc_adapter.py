import logging
from generated import mqfm_pb2, mqfm_pb2_grpc
from youtube_dakwah_streaming.infrastructure.cache_adapter import YoutubeDakwahStreamingCacheAdapter
from youtube_dakwah_streaming.infrastructure.scraper_adapter import YoutubeDakwahStreamingScraperAdapter
from youtube_dakwah_streaming.application.use_case import GetYoutubeDakwahStreamingUseCase

logger = logging.getLogger(__name__)


class YoutubeDakwahStreamingGrpcServicer(mqfm_pb2_grpc.YoutubeDakwahStreamingGrpcServicer):
    def GetYoutubeDakwahStreaming(self, request, context):
        cache = YoutubeDakwahStreamingCacheAdapter()
        scraper = YoutubeDakwahStreamingScraperAdapter()
        use_case = GetYoutubeDakwahStreamingUseCase(cache=cache, scraper=scraper)
        data = use_case.execute()

        return mqfm_pb2.YoutubeDakwahStreamingResponse(
            youtube_url=data.get("youtube_url") or "",
            title=data.get("title") or "",
        )
