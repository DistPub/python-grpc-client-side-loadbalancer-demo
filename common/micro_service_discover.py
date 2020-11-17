import json
import threading


class ServiceUnavailable(Exception):
    pass


class SingletonType(type):
    _instance = {}
    _lock = threading.Lock()

    def __call__(cls, service_name, *args, **kwargs):
        with cls._lock:
            if service_name not in cls._instance:
                cls._instance[service_name] = super(SingletonType, cls).__call__(service_name, *args, **kwargs)
            return cls._instance[service_name]

    @classmethod
    def get_instance(mcs, service_name):
        return mcs._instance.get(service_name)


class MicroServiceDiscover(metaclass=SingletonType):
    _lock = threading.Lock()

    def __init__(self, service_name, client):
        # 初始化节点和选择器
        self.registered_endpoint_list = []
        self.endpoint_select_dict = dict()
        self.register_endpoints(endpoint_set=client.get_list(service_name))
        # watch 监控
        client.add_watch_callback(key=service_name, callback=self.update_endpoints, progress_notify=True)

    def update_endpoints(self, watched_response):
        """更新节点"""
        print(f'update endpoints')
        watched_event = watched_response.events[0]
        endpoints_bytes = watched_event.value
        try:
            update_endpoint_list = json.loads(endpoints_bytes)
            if not isinstance(update_endpoint_list, list):
                raise TypeError
        except (TypeError, ValueError):  # pylint:disable=unused-variable
            return

        remove_endpoint_set = set(self.registered_endpoint_list) - set(update_endpoint_list)
        register_endpoint_set = set(update_endpoint_list) - set(self.registered_endpoint_list)
        # 移除失效的
        print(f'remove endpoints: {remove_endpoint_set}')
        self.remove_endpoints(endpoint_set=remove_endpoint_set)

        print(f'register endpoints: {register_endpoint_set}')
        # 注册新的
        self.register_endpoints(endpoint_set=register_endpoint_set)

    def remove_endpoints(self, endpoint_set):
        """移除节点"""
        for endpoint in endpoint_set:
            self.registered_endpoint_list.remove(endpoint)
            del self.endpoint_select_dict[endpoint]

    def register_endpoints(self, endpoint_set):
        """注册节点"""
        for endpoint in endpoint_set:
            self.registered_endpoint_list.append(endpoint)
            self.endpoint_select_dict[endpoint] = 0

    def get_endpoint(self):
        """获取节点"""
        with self._lock:
            endpoint_sort_list = sorted(self.endpoint_select_dict.items(), key=lambda x: x[1], reverse=False)
            if not endpoint_sort_list:
                raise ServiceUnavailable()
            endpoint, endpoint_count = endpoint_sort_list[0]
            if endpoint_count > 0:
                for each_endpoint in self.endpoint_select_dict:
                    self.endpoint_select_dict[each_endpoint] = 0
            self.endpoint_select_dict[endpoint] = 1
            return endpoint
