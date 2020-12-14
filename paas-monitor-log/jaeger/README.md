1. 部署 jaeger operator:  https://github.com/jaegertracing/jaeger-operator
2. 编写 jaeger 资源文件，创建

生产环境 jaeger 独立集群，服务集群部署 jaeger agent daemonset , 配置 istio-system 下 zipkin service 指到 jaeger
