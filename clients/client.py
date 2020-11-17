import grpc

from common.micro_service_discover import ServiceUnavailable
from protos import service_pb2_grpc, service_pb2


def request(endpoint):
    name = input('Your name:')

    try:
        with grpc.insecure_channel(endpoint) as channel:
            stub = service_pb2_grpc.GreeterStub(channel)
            response = stub.SayHello(service_pb2.HelloRequest(name=name))
            print(f'receive response: {response.message}')
    except grpc.RpcError as error:
        # grpc 异常处理
        if error.code() == grpc.StatusCode.UNAVAILABLE:  # pylint:disable=no-member
            #  网络等原因异常,需要重试
            raise ServiceUnavailable()
