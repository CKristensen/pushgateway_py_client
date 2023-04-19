import time
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, push_to_gateway

global_counter = {}
global_gauges = {}
global_histograms = {}


class MetricsClient:
    def __init__(
        self,
        pushgateway_url: str,
        job_name: str,
        push_function=push_to_gateway,
    ):
        self._url = pushgateway_url
        self._job_name = job_name
        self._registry = CollectorRegistry()
        self._push_function = push_function
        self._gauges = (lambda: global_gauges)()
        self._counters = (lambda: global_counter)()
        self._histograms = (lambda: global_histograms)()

    def __push(self):
        """
        Push all metrics to the pushgateway
        :return:
        """
        self._push_function(self._url, job=self._job_name, registry=self._registry)

    def increment(self, metric: str, value: float = 1, labels: dict = {}):
        """
        Push a counter metric to the pushgateway
        :param labels:
        :param metric:
        :param value:
        :return:
        """
        counter_label_names = list(labels.keys())

        def __add_counter(metric_name: str, help_text: str):
            """
            Add a counter metric to the registry
            :param metric_name:
            :param help_text:
            :return:
            """
            if metric_name not in global_counter:
                global_counter[metric_name] = Counter(
                    metric_name,
                    help_text,
                    registry=self._registry,
                    labelnames=counter_label_names,
                )

        def __increment_counter(metric_name: str, value_: float = 1):
            """
            Increment a counter metric by a specific value
            :param metric_name:
            :param value_:
            :return:
            """
            global_counter[metric_name].labels(**labels).inc(value_)

        __add_counter(metric, "Counter metric")
        __increment_counter(metric, value)
        self.__push()

    def gauge(self, metric: str, value: float, labels: dict = {}):
        """
        Push a gauge metric to the pushgateway
        :param labels:
        :param metric:
        :param value:
        :return:
        """

        gauge_label_names = list(labels.keys())

        def __add_gauge(metric_name: str, help_text: str):
            """
            Add a gauge metric to the registry
            :param metric_name:
            :param help_text:
            :return:
            """
            if metric_name not in global_gauges:
                global_gauges[metric_name] = Gauge(
                    metric_name,
                    help_text,
                    registry=self._registry,
                    labelnames=gauge_label_names,
                )

        def __set_gauge(metric_name: str, metric_value: float):
            """
            Set a gauge metric to a specific value
            :param metric_name:
            :param metric_value:
            :return:
            """
            global_gauges[metric_name].labels(**labels).set(metric_value)

        __add_gauge(metric, "Gauge metric")
        __set_gauge(metric, value)
        self.__push()

    def histogram(self, metric: str, value: float, labels: dict = {}, buckets = None):
        """
        Push a histogram metric to the pushgateway
        :param buckets:
        :param labels:
        :param metric:
        :param value:
        :return:
        """

        histogram_label_names = list(labels.keys())
        if metric not in global_histograms:
            global_histograms[metric] = Histogram(
                metric,
                "Histogram metric",
                registry=self._registry,
                labelnames=histogram_label_names,
                buckets=Histogram.DEFAULT_BUCKETS if not buckets else buckets,
            )
        global_histograms[metric].labels(**labels).observe(value)
        self.__push()

    def timeit(self, metric, labels):
        """
        Decorator to time a function and push the execution time to the pushgateway. (seconds)
        :param labels:
        :param metric:
        """

        def decorator(function):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = function(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                self.gauge(metric, execution_time, labels)
                return result

            return wrapper

        return decorator
