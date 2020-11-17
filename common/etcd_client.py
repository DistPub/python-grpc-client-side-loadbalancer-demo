import json
import threading
import time

import etcd3
import grpc
from etcd3.client import EtcdTokenCallCredentials


class Etcd3ValueIncorrent(Exception):
    pass


class Etcd3ClientProxy(etcd3.Etcd3Client):
    RENEW_CREDENTIAL_INTERVAL_TIME = 4 * 60

    def __init__(self, *args, user=None, password=None, **kwargs):
        self.user = user
        self.password = password
        super().__init__(*args, user=user, password=password, **kwargs)
        self.auto_renew_credential()

    def auto_renew_credential(self):
        thread = threading.Thread(name='auto_renew_credential', target=self.renew_credential_loop)
        thread.daemon = True
        thread.start()

    def renew_credential_loop(self):
        while True:
            time.sleep(self.RENEW_CREDENTIAL_INTERVAL_TIME)
            auth_request = etcd3.etcdrpc.AuthenticateRequest(
                name=self.user,
                password=self.password
            )
            resp = self.auth_stub.Authenticate(auth_request, self.timeout)
            self.metadata = (('token', resp.token),)
            self.call_credentials = grpc.metadata_call_credentials(EtcdTokenCallCredentials(resp.token))

    def get_list(self, key, **kwargs):
        value, _ = self.get(key, **kwargs)
        value_list = []

        if value is not None:
            try:
                value_list = json.loads(value.decode('utf-8'))
                if not isinstance(value_list, list):
                    raise TypeError()
            except (TypeError, ValueError):
                raise Etcd3ValueIncorrent()

        return value_list

    def put_list(self, key, value, lease=None, prev_kv=False):
        if not isinstance(value, list):
            raise Etcd3ValueIncorrent()

        return self.put(key, json.dumps(value), lease, prev_kv)
