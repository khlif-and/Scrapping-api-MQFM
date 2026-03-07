import logging
from generated import mqfm_pb2, mqfm_pb2_grpc
from otp.infrastructure.cache_adapter import OTPCacheAdapter
from otp.infrastructure.email_adapter import OTPEmailAdapter
from otp.application.use_case import GenerateOTPUseCase, VerifyOTPUseCase

logger = logging.getLogger(__name__)


class OTPGrpcServicer(mqfm_pb2_grpc.OTPGrpcServicer):
    def GenerateOTP(self, request, context):
        cache = OTPCacheAdapter()
        email_sender = OTPEmailAdapter()
        use_case = GenerateOTPUseCase(cache=cache, email_sender=email_sender)
        result = use_case.execute(request.email)

        return mqfm_pb2.OTPResponse(
            success=result["success"],
            message=result["message"],
        )

    def VerifyOTP(self, request, context):
        cache = OTPCacheAdapter()
        use_case = VerifyOTPUseCase(cache=cache)
        result = use_case.execute(request.email, request.otp_code)

        return mqfm_pb2.OTPResponse(
            success=result["success"],
            message=result["message"],
        )
