import grpc
from concurrent import futures
import logging

logger = logging.getLogger(__name__)


def create_grpc_server(port: int = 50051, max_workers: int = 10):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    return server, port


def start_grpc_server(server, port: int = 50051):
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"gRPC server started on port {port}")
    return server
