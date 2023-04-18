from pushgateway_py_client import MetricsClient
import time
import random

labels = {'env': 'pre', 'app': 'fake_app'}
metrics = MetricsClient(pushgateway_url='localhost:9091', job_name="batchA")


def fail_or_success_randomly(i: int):
    if i == 0:
        metrics.increment('job_count_fail', 1, labels)
        return 0
    metrics.increment('job_count_success', 1, labels)
    return 1


def some_gauge():
    metrics.gauge('job_last_success_unixtime', time.time(), labels)


@metrics.timeit('fake_app_duration_seconds', labels)
def fake_app() -> int:
    time.sleep(random.randint(1, 5))
    fail_or_success_randomly(random.randint(0, 1))
    some_gauge()
    return 1


if __name__ == '__main__':
    while True:
        print("ping...", end=" ")
        fake_app()
        print("pong...")
