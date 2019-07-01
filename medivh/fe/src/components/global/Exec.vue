<template>
<modal :show="visible">
  <div class="exec-result">
    <div class="list">
      <table class="table" v-if="!showStack">
        <tbody>
          <tr>
            <th>IP</th>
            <th>执行信息</th>
            <th>执行结果</th>
            <th>stack</th>
          </tr>
          <tr v-for="(r, idx) in execResult">
            <td>{{r.ip}}</td>
            <td>{{r.message}}</td>
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
      <pre v-else>{{currStack | json}}</pre>
    </div>
    <div class="btns">
      <span>{{execing ? '执行中 ...' : '执行完毕'}}</span>
      <button
        v-show="!execing || showStack"
        type="button"
        class="btn btn-primary pull-right"
        @click="onCloseResult">{{!showStack ? '确定' : '返回'}}</button>
    </div>
  </div>
</modal>
</template>

<script>
import http from '@/utils/networking'
import Modal from '@/components/global/Modal'
import {golive as apis} from '@/constants/api'

let poll = null

export default {
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    id: {
      type: [String, Number],
      default: ''
    }
  },

  components: {
    Modal
  },

  data () {
    return {
      showStack: false,
      execing: true,
      currStack: {},
      execResult: []
    }
  },

  watch: {
    visible (val) {
      if (val) {
        this.poll(this.id)
      }
    }
  },

  beforeDestroy () {
    this.stopPoll()
    poll = null
  },

  methods: {
    stopPoll () {
      poll && poll.stop()
    },

    poll (id) {
      this.stopPoll()
      poll = new Poll(apis.execResult, {id})
      this.execing = true
      this.showResult = true

      poll.start(data => {
        if (data.finish) {
          this.execing = false
        }
        this.execResult = data.list
      })
    },

    onStack (idx) {
      this.currStack = this.execResult[idx].stack
      this.showStack = true
    },

    onCloseResult () {
      if (!this.showStack) {
        this.stopPoll()
        this.$emit('update:visible', false)
        this.execResult = []
        this.$emit('close')
      } else {
        this.showStack = false
        this.currStack = ''
      }
    }
  },

  filters: {
    statusToText (status) {
      return status ? '成功' : '失败'
    }
  }
}

const INTERVAL = 5 * 1000

function Poll(url, params) {
  this.url = url
  this.params = params
  this.timeId = null
}

Poll.prototype.start = function (callback) {
  this.callback = callback
  this.fetch()
  this.timeId = setInterval(() => {
    this.fetch()
  }, INTERVAL)
}

Poll.prototype.stop = function () {
  clearInterval(this.timeId)
}

Poll.prototype.fetch = function () {
  http.doGet(this.url, this.params).then(({data}) => {
    if (data.finish) {
      this.stop()
    }
    this.callback(data)
  })
}
</script>

<style lang="less">
.exec-result {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  margin: auto;
  width: 700px;
  height: 450px;
  padding: 20px;
  border-radius: 4px;
  background-color: #fff;

  .list {
    height: 355px;
    margin-bottom: 20px;
    overflow: auto;
  }

  li {
    margin-bottom: 10px;
  }

  .message {
    cursor: pointer;
  }

  .stack {
    cursor: pointer;
  }
}
</style>
