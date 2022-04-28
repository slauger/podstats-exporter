# podstats-exporter

Expose the podstats API as prometheus metrics endpoint.

Currently this is a Proof of concept only!

## Setup dependencies

```
pip3 install -r requirements.txt
```

## Run exporter

Currently the exporter only listens to the current namespace.

```
python3 podstats-exporter.py
```

## Scrape

```
-bash$ curl localhost:8080
podmetrics_container_cpu_usage{container="kube-rbac-proxy",namespace="openshift-monitoring",pod="thanos-querier-6544ddbc8b-2jnc9"} 0.001
podmetrics_container_cpu_usage{container="oauth-proxy",namespace="openshift-monitoring",pod="thanos-querier-6544ddbc8b-2jnc9"} 0.001
podmetrics_container_cpu_usage{container="kube-rbac-proxy-rules",namespace="openshift-monitoring",pod="thanos-querier-6544ddbc8b-2jnc9"} 0.001
...
```
