<template>
<div class="hosts">
  <table class="table">
    <tbody>
      <tr>
        <th>ip</th>
        <th>执行时间</th>
        <th>描述</th>
        <th>执行结果</th>
        <th>stack</th>
      </tr>
      <tr v-for="(r, idx) in result">
        <td>{{r.host_ip}}</td>
        <td>{{r.run_time | date(true)}}</td>
        <td>{{r.description}}</td>
        <td>
          <span
            class="label"
            :class="r.is_success ? 'bg-green' : 'bg-red'"
          >{{r.is_success | statusToText}}</span>
        </td>
        <td>
          <a
            class="stack"
            @click="onStack(idx)">查看</a>
        </td>
      </tr>
    </tbody>
  </table>

  <modal
    :show="showStack"
    @click="showStack = false">
    <div class="stack-box" @click.stop>
      <pre>{{currStack | json}}</pre>
    </div>
  </modal>
</div>
</template>

<script>
import http from '@/utils/networking'
import {golive as apis} from '@/constants/api'
import Modal from '@/components/global/Modal'

export default {
  components: {
    Modal
  },

  data () {
    return {
      stageId: '',
      hostId: '',
      result: [],

      currStack: '',
      showStack: false
    }
  },

  created () {
    let params = this.$route.params
    let stageId = this.stageId = params.stageId
    let hostId = this.hostId = params.hostId

    http.doGet(apis.hostExecResult, {stageId, hostId}).then(({data}) => {
      this.result = data.results
    })
  },

  methods: {
    onStack (idx) {
      this.currStack = this.result[idx].result
      this.showStack = true
    }
  },

  filters: {
    statusToText (status) {
      return status ? '成功' : '失败'
    }
  }
}
</script>

<style lang="less" scoped>
.hosts {
  background-color: #fff;
}

th,
td {
  text-align: center;
}

.stack {
  cursor: pointer;
}

.stack-box {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  margin: auto;
  width: 600px;
  height: 400px;
  padding: 20px;
  border-radius: 4px;
  background-color: #fff;

  pre {
    height: 360px;
    padding-bottom: 20px;
    overflow: auto;
  }
}
</style>
