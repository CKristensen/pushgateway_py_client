[![Publish Python 🐍 distributions 📦 to PyPI and TestPyPI with poetry](https://github.com/CKristensen/pushgateway_py_client/actions/workflows/publish-python-poetry.yml/badge.svg?branch=main)](https://github.com/CKristensen/pushgateway_py_client/actions/workflows/publish-python-poetry.yml)
# Simple Pushgateway Python Client
Python client for Pushgateway.  
Pushgateway allows you to track state on specific metrics.  
Often times the configuration and complexity of this can be a bit intimidating for new users.  
With this client, you can quickly and easily get started tracking metrics without having to worry about things like state.

### Prometheus Pushgateway docs https://prometheus.io/docs/practices/pushing/

## Getting Started
~ `pip install pushgateway_py_client`

### Example
```
from pushgateway_py_client import MetricsClient

metrics = MetricsClient(pushgateway_url='localhost:9091', job_name="batchA")

labels = {'env': 'pre', 'app': 'fake_app'}

metrics.increment('job_count_fail', 123, labels)
metrics.increment('job_count_success', 321, labels)
metrics.gauge('job_last_success_unixtime', 1203198273, labels)


@metrics.timeit('fake_app_duration_seconds', labels)
def fake_app() -> int:
    pass
```

### Note:
If the same meric is running different instances at the same time you should add a label that can distinguish the different instances.  
This is because the pushgateway will only keep the most recent value for a metric with the same name and labels.
````
# Example
import os
import socket

labels = {'host': socket.gethostbyname(socket.gethostname()),
          'pid': os.getpid()}
````

### License
This project is licensed under the MIT License - see the LICENSE.md file for details


