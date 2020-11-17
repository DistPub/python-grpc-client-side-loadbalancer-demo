class MicroServiceManageCenter:
    def __init__(self, service_ip, service_port, client, lock_prefix=None):
        self.client = client
        self.lock_prefix = lock_prefix
        self.endpoint = f'{service_ip}:{service_port}'

    def register_service(self, name):
        with self.client.lock(name, lock_prefix=self.lock_prefix):
            value_list = self.client.get_list(name)
            if self.endpoint not in value_list:
                value_list.append(self.endpoint)
                self.client.put_list(name, value_list)

    def cancel_service(self, name):
        with self.client.lock(name, lock_prefix=self.lock_prefix):
            value_list = self.client.get_list(name)
            if self.endpoint in value_list:
                value_list.remove(self.endpoint)
                self.client.put_list(name, value_list)
