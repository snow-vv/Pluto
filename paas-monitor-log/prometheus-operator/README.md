### 更新primary 集群prometheus(需翻墙)

helm upgrade -f ./values.override.primary.yaml prometheus-operator stable/prometheus-operator

### 更新secondary 集群prometheus(需翻墙)

helm upgrade -f ./values.override.secondary.yaml prometheus-operator stable/prometheus-operator


Secondary集群的Prometheus通过内网LB(172.16.50.9:9090)暴露给Primary集群的Grafana