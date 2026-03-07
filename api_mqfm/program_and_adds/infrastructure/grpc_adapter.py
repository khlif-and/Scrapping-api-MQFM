import logging
from generated import mqfm_pb2, mqfm_pb2_grpc
from program_and_adds.infrastructure.cache_adapter import ProgramAndAddsCacheAdapter
from program_and_adds.infrastructure.scraper_adapter import ProgramAndAddsScraperAdapter
from program_and_adds.application.use_case import GetProgramAndAddsUseCase

logger = logging.getLogger(__name__)


class ProgramAndAddsGrpcServicer(mqfm_pb2_grpc.ProgramAndAddsGrpcServicer):
    def GetProgramAndAdds(self, request, context):
        cache = ProgramAndAddsCacheAdapter()
        scraper = ProgramAndAddsScraperAdapter()
        use_case = GetProgramAndAddsUseCase(cache=cache, scraper=scraper)
        data = use_case.execute()

        return mqfm_pb2.ProgramAndAddsResponse(
            programs=[
                mqfm_pb2.ProgramAndAddsItem(title=p["title"], image_url=p["image_url"])
                for p in data["programs"]
            ]
        )
