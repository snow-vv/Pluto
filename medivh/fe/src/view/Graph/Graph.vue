<template>
<div class="graph">
  <div ref="graph"></div>
</div>
</template>

<script>
import echarts from 'echarts'
import 'echarts/lib/chart/bar'
// 引入提示框和标题组件
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'

import http from '@/utils/networking'
import {graph} from '@/constants/api'

export default {
  data () {
    return {

    }
  },

  mounted () {
    http.doGet(graph.service).then(({data}) => {
      this.draw(data.nodes, data.list)
    })
  },

  methods: {
    transNode (nodes) {
      return nodes.map(n => {
        return {
          id: n,
          name: n,
          x: null,
          y: null,
          draggable: true,
          category: n,
          label: {
            normal: {
              show: true
            }
          },
          tooltip: {
            formatter: '{b}'
          }
        }
      })
    },

    transLink (links) {
      return links.map(l => {
        return {
          source: l.src,
          target: l.target,
          weight: l.weight,
          lineStyle: {
            normal: {
              width: l.wide * 0.5,
              curveness: 0.15
            }
          }
        }
      })
    },

    draw (nodes, links) {
      let chart = echarts.init(this.$refs.graph)
      let categories = nodes.map(n => ({name: n}))
      nodes = this.transNode(nodes)
      links = this.transLink(links)

      let option = {
        tooltip: {},
        animation: false,
        series: [
          {
            name: '服务关系图',
            type: 'graph',
            layout: 'force',
            symbolSize: 50,
            roam: true,
            focusNodeAdjacency: true,
            edgeSymbol: ['circle', 'arrow'],
            edgeSymbolSize: [0, 10],
            tooltip: {
              formatter (p) {
                return `${p.name} (${p.data.weight})`
              }
            },
            force: {
              repulsion: 2500
            },
            categories: categories,
            data: nodes,
            links: links
          }
        ]
      }

      chart.setOption(option)
    }
  }
}
</script>

<style lang="less" scoped>
.graph {
  position: absolute;
  left: 245px;
  right: 15px;
  top: 105px;
  bottom: 15px;
  background-color: #fff;

  > div {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
  }
}
</style>
