from protos import service_pb2_grpc, service_pb2


class Greeter(service_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print(f'receive request: {request.name}')
        return service_pb2.HelloReply(message=f'Hello, {request.name}!')
