"""PodMetrics exporter"""

import os
import time
import json
import subprocess
import prometheus_client
from prometheus_client import start_http_server, CollectorRegistry, Gauge, Enum
from kubernetes.utils.quantity import parse_quantity

class PodMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        # reset the underlying Prometheus registry
        collectors = list(prometheus_client.registry.REGISTRY._collector_to_names.keys())
        for collector in collectors:
          prometheus_client.registry.REGISTRY.unregister(collector)

        # Prometheus metrics to collect
        podmetrics_container_cpu_usage = Gauge('podmetrics_container_cpu_usage', 'Container CPU usage', ['pod', 'container', 'namespace'])
        podmetrics_container_memory_usage = Gauge('podmetrics_container_memory_usage', 'Container memory usage', ['pod', 'container', 'namespace'])
        podmetrics_pod_cpu_usage = Gauge('podmetrics_pod_cpu_usage', 'Pod CPU usage', ['pod', 'namespace'])
        podmetrics_pod_memory_usage = Gauge('podmetrics_pod_memory_usage', 'Pod memory usage', ['pod', 'namespace'])

        # Query API via CLI
        output = subprocess.check_output(['oc', 'get', 'podmetrics', '-o', 'json'])
        metrics = json.loads(output)

        # Update Prometheus metrics with application metrics
        for pod in metrics['items']:
          pod_cpu_usage = 0
          pod_memory_usage = 0

          for container in pod['containers']:
            if container['name'] == 'POD':
              continue

            container_cpu_usage = parse_quantity("1m")
            container_memory_usage = int(int(parse_quantity("128m")*1000*1000))

            pod_cpu_usage = pod_cpu_usage + container_cpu_usage
            pod_memory_usage = pod_memory_usage + container_memory_usage

            podmetrics_container_cpu_usage.labels(pod['metadata']['name'], container['name'], pod['metadata']['namespace']).set(container_cpu_usage)
            podmetrics_container_memory_usage.labels(pod['metadata']['name'], container['name'], pod['metadata']['namespace']).set(container_memory_usage)

          podmetrics_pod_cpu_usage.labels(pod['metadata']['name'], pod['metadata']['namespace']).set(pod_cpu_usage)
          podmetrics_pod_memory_usage.labels(pod['metadata']['name'], pod['metadata']['namespace']).set(pod_memory_usage)


def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "8080"))

    pod_metrics = PodMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    pod_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
