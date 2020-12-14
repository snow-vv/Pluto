### PAAS系统监控和日志
主要由3部分组成:
- prometheus-operatour
- fluentd
- istio

## prometheus-operator
- values.override.primary.yaml 是主集群helm install 时override的值, DingDing通知等配置信息在这里
- values.override.secondary.yaml 是secondary集群helm install 时override的值, secondary不包含grafana, primary包含grafa
- 以.ServiceMonitor.yaml和.PodMonitor.yaml结尾的是Prometheus-Operator支持的两种监控类型，对应的是服务的监控和pod的监控(转换成prometheus配置), 主要是istio的和sidecar的
- 以.rules.yaml结尾的是各种报警规则, 通过命名规则大体识别出是哪类报警
- .grafana.json就是自定义的监控模板，主要是fluentd和服务的

## fluentd
- 核心在values.*.yaml里,
- values.prod.primary.yaml是主集群用到的配置
- values.prod.secondary.yaml是secondary集群用的配置
- values.test.yaml是测试环境用到的配置

#### 关于fluentd.services说明
- fluend以daemonset形式安装, 默认安装后不会创建service
- fluentd除了收集日志文件外, 还接受istio上过的istio-access日志, 因此需要创建fluentd service来提供其它服务调用

#### 关于Container log
- Fluentd: Container log的日期格式 time_format "%Y-%m-%dT%H:%M:%S.%NZ", Fluent识别出来的record时间为当前时间
- 发送到ES: Container log的日期格式 time_key_format "%Y-%m-%dT%H:%M:%S.%NZ" 可以被Elasticsearch识别

#### 关于python的业务日志
- Fluentd: 日志时间格式 time_format "%Y-%m-%d %H:%M:%S,%N", Fluentd能识别出来record时间为日志里的时间
- 发送到ES: 虽然指定了 time_key_format "%Y-%m-%d %H:%M:%S,%N", 能不能被识别为日期格式, 需要转换成iso8601(6)


## istio
- 主要是获取mixer的数据
- mix.yaml是收集mixer数据到prometheus, 包含istio提供的但腾讯不提供的和自定义的
- log.yaml 是收集数据到fluentd，再转发到日志服务器，再转发到es(istio-http-access日志的来源)
