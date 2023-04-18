from time import sleep
from pushgateway_py_client import MetricsClient
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
        pushgateway_metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )

        pushgateway_metrics.gauge("nameA", 442, labels)
        # confirm that the pushgateway was called
        self.assertEqual(len(executions), 1)
        # confirm that the job name was passed to the pushgateway
        self.assertEqual(
            pushgateway_metrics._gauges["nameA"]
            .labels(**labels)
            ._value.get(),
            442,
        )
        for execution in executions:
            self.assertEqual(execution["job"], "batchA")
            self.assertEqual(execution["url"], "foo:bar")

        pushgateway_metrics.gauge("nameA", 1337, labels)
        self.assertEqual(
            pushgateway_metrics._gauges["nameA"]
            .labels(**labels)
            ._value.get(),
            1337,
        )
        self.assertEqual(len(executions), 2)

    def test_push_counter(self):
        pushgateway_metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )
        pushgateway_metrics.increment("nameB", 3, labels)
        self.assertEqual(
            pushgateway_metrics._counters["nameB"]
            .labels(**labels)
            ._value.get(),
            3,
        )

        pushgateway_metrics.increment("nameB", 3, labels)
        pushgateway_metrics.increment("nameB", 3, labels)

        self.assertEqual(
            pushgateway_metrics._counters["nameB"]
            .labels(**labels)
            ._value.get(),
            9,
        )
        # confirm that the job name was passed to the pushgateway
        for execution in executions:
            self.assertEqual(execution["job"], "batchA")
            self.assertEqual(execution["url"], "foo:bar")

        pushgateway_metrics.increment("nameB", 3, labels)
        self.assertEqual(
            pushgateway_metrics._counters["nameB"]
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
        pushgateway_metrics = MetricsClient(
            pushgateway_url="foo:bar",
            job_name="batchA",
            push_function=MockPushGateway.fake_push_to_gateway,
        )

        #  time with pushgateway timeit and set name to abc
        @pushgateway_metrics.timeit("nameC", labels)
        def dummy_function():
            sleep(time_val / fraction)

        time_val = 3
        fraction = 100

        for _ in range(3):
            dummy_function()
            self.assertEqual(
                pushgateway_metrics._gauges["nameC"]._name,
                "nameC",
            )
            self.assertEqual(
                pushgateway_metrics._gauges[
                    "nameC"
                ]._labelnames[0],
                "env",
            )


if __name__ == "__main__":
    unittest.main()
