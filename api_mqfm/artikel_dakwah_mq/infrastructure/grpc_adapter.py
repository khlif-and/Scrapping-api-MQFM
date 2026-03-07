import logging
from generated import mqfm_pb2, mqfm_pb2_grpc
from artikel_dakwah_mq.infrastructure.cache_adapter import ArtikelDakwahMqCacheAdapter
from artikel_dakwah_mq.infrastructure.scraper_adapter import ArtikelDakwahMqScraperAdapter
from artikel_dakwah_mq.application.use_case import GetArtikelDakwahMqUseCase

logger = logging.getLogger(__name__)


class ArtikelDakwahMqGrpcServicer(mqfm_pb2_grpc.ArtikelDakwahMqGrpcServicer):
    def GetArtikelDakwahMq(self, request, context):
        cache = ArtikelDakwahMqCacheAdapter()
        scraper = ArtikelDakwahMqScraperAdapter()
        use_case = GetArtikelDakwahMqUseCase(cache=cache, scraper=scraper)
        data = use_case.execute()

        return mqfm_pb2.ArtikelDakwahMqResponse(
            channel_name=data["channel_name"],
            tagline=data["tagline"],
            website=data["website"],
            programs=[
                mqfm_pb2.ProgramItem(program=p["program"], schedule=p["schedule"])
                for p in data["programs"]
            ],
            contents=[
                mqfm_pb2.ContentItem(
                    title=c["title"],
                    link=c["link"],
                    image=c.get("image") or ""
                )
                for c in data["contents"]
            ],
        )
