from time import sleep
from src.pushgateway_py_client import MetricsClient
import unittest

executions = []


class MockPushGateway:
    @staticmethod
    def fake_push_to_gateway(url, job, registry):
        executions.append({"url": url, "job": job, "registry": registry})


labels = {"env": "pre", "hostname": "fake_host", "pid": "fake_pid"}


class TestMetricsClient(unittest.TestCase):
    def setUp(self):
        executions.clear()

    def test_push_gauge(self):
        metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )

        metrics.gauge("nameA", 442, labels)
        # confirm that the pushgateway was called
        self.assertEqual(len(executions), 1)
        # confirm that the job name was passed to the pushgateway
        self.assertEqual(
            metrics._gauges["nameA"]
            .labels(**labels)
            ._value.get(),
            442,
        )
        for execution in executions:
            self.assertEqual(execution["job"], "batchA")
            self.assertEqual(execution["url"], "foo:bar")

        metrics.gauge("nameA", 1337, labels)
        self.assertEqual(
            metrics._gauges["nameA"]
            .labels(**labels)
            ._value.get(),
            1337,
        )
        self.assertEqual(len(executions), 2)

    def test_push_counter(self):
        metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )
        metrics.increment("nameB", 3, labels)
        self.assertEqual(
            metrics._counters["nameB"]
            .labels(**labels)
            ._value.get(),
            3,
        )

        metrics.increment("nameB", 3, labels)
        metrics.increment("nameB", 3, labels)

        self.assertEqual(
            metrics._counters["nameB"]
            .labels(**labels)
            ._value.get(),
            9,
        )
        # confirm that the job name was passed to the pushgateway
        for execution in executions:
            self.assertEqual(execution["job"], "batchA")
            self.assertEqual(execution["url"], "foo:bar")

        metrics.increment("nameB", 3, labels)
        self.assertEqual(
            metrics._counters["nameB"]
            .labels(**labels)
            ._value.get(),
            12,
        )
        parallel_pushgateway_metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )

        self.assertEqual(
            parallel_pushgateway_metrics._counters["nameB"]
            .labels(**labels)
            ._value.get(),
            12,
        )

    def test_execution_time(self):
        metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )

        #  time with pushgateway timeit and set name to abc
        @metrics.timeit("nameC", labels)
        def dummy_function():
            sleep(time_val / fraction)

        time_val = 3
        fraction = 100

        for _ in range(3):
            dummy_function()
            self.assertEqual(
                metrics._gauges["nameC"]._name,
                "nameC",
            )
            self.assertEqual(
                metrics._gauges[
                    "nameC"
                ]._labelnames[0],
                "env",
            )

    def test_push_histogram(self):
        metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )

        def get_bucket(upper_bound):
            index = [index for index, up in enumerate(metrics._histograms["nameD"].labels(**labels)._upper_bounds) if
                     up > upper_bound][0]
            return metrics._histograms["nameD"].labels(**labels)._buckets[index]._value

        # Test observation 3, 1 time
        metrics.histogram("nameD", 3, labels)
        bucket3 = get_bucket(3)

        self.assertEqual(bucket3, 1)

        # Test observation 30, 10 times
        for _ in range(10):
            metrics.histogram("nameD", 30, labels)

        bucket30 = get_bucket(30)
        self.assertEqual(bucket30, 10)

        # confirm that the job name was passed to the pushgateway
        for execution in executions:
            self.assertEqual(execution["job"], "batchA")
            self.assertEqual(execution["url"], "foo:bar")


if __name__ == "__main__":
    unittest.main()
