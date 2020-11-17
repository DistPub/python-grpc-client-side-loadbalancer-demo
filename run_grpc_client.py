#!/usr/bin/env python3
from time import sleep

from clients.client import request
from common.etcd_client import Etcd3ClientProxy
from common.micro_service_discover import MicroServiceDiscover, ServiceUnavailable
from common.utils import get_arguments_parser


def main(etcd_host, etcd_port, etcd_username, etcd_password, etcd_app_path):
    service_name = f'{etcd_app_path}Greeter'
    grpc_service = MicroServiceDiscover.get_instance(service_name)

    if not grpc_service:
        etcd3_client = Etcd3ClientProxy(host=etcd_host, port=etcd_port, user=etcd_username, password=etcd_password)
        grpc_service = MicroServiceDiscover(service_name=service_name, client=etcd3_client)

    while True:
        try:
            request(grpc_service.get_endpoint())
        except ServiceUnavailable:
            print(f'service unavailable, retry!')
            sleep(3)


if __name__ == '__main__':  # coverage:ignore=
    parser = get_arguments_parser()
    options = parser.parse_args()
    main(options.etcd_host, options.etcd_port, options.etcd_username, options.etcd_password, options.etcd_app_path)
