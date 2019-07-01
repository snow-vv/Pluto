<template>
<div class="execution">
  <div class="box box-solid">
    <div class="box-body">
      <ul class="list">
        <li class="list-item">
          <span>描述:</span>
          <span>{{plan.name}}</span>
        </li>
        <li class="list-item">
          <span>期望上线时间:</span>
          <span>{{plan.golive_expected_time | date(true)}}</span>
        </li>
        <li class="list-item">
          <span>备注:</span>
          <span>{{plan.notes}}</span>
        </li>
      </ul>
    </div>
  </div>

  <div
    v-for="(s, sidx) in plan.stages"
    :key="s.id"
    class="box box-solid">
    <div class="box-header">{{s.service.name}}</div>
    <div class="box-body stage">
      <div class="stage-info">
        <ul class="list">
          <li v-for="t in s.tasks" class="list-item">
            <span>{{t.function_id | idToName}}:</span>
            <span>
            <span
                v-if="getTaskById(t.function_id).type==TASK_TYPE.INPUT"
            >{{t | toValue}}</span>
            <i v-else class="fa fa-check"></i>
          </span>
          </li>
        </ul>
        <!-- 回滚 -->
        <div class="rollback-title" @click="onShowCodeBack(sidx)">上线失败，回滚代码？</div>
        <div class="form-group" v-show="s.isshow">
          <div class="form-value rollback-box">
            <div class="back-list">
              <search-select
                  :data="s.commit_ids"
                  :current="s.commit_id"
                  @select="commit => onSelectCommit(sidx, commit)"
              />
            </div>
            <div class="back-list">
              <input class="hash-input form-control" v-model="s.input_id">
            </div>
            <div class="back-list">
              <button type="button" class="btn btn-primary" @click="onCommitSave(sidx)">提交</button>
            </div>
          </div>
        </div>
      </div>


      <div class="stage-op">
        <div class="op-logs">
          <ul>
            <li
              v-for="h in s.hosts"
              :key="h.host_id">
              <router-link :to="`/executions/stage/${s.id}/host/${h.host_id}`">
                <span>{{h.host_name}}</span>
                <span>{{h.status.desc}}</span>
              </router-link>
            </li>
          </ul>
        </div>

        <div class="op-ops">
          <button
            v-for="btn in s.service_execution_info"
            type="button"
            class="btn btn-block btn-default"
            @click="onExec(sidx, btn.id)"
          >{{btn.name}}</button>
        </div>
      </div>
    </div>
  </div>

  <div class="op-all clearfix">
    <div class="pull-right">
      <button
        type="button"
        class="btn btn-success add"
        @click="onReleaseDone()"
        v-if="plan.status.value==3"
      >上线完成</button>
      <button
        v-for="btn in plan.execution_info_types"
        type="button"
        class="btn btn-primary add"
        @click="onExecAll(btn.value)"
      >{{btn.desc}}</button>
    </div>
  </div>

  <exec-result
    :visible.sync="showResult"
    :id="execResultId"
    @close="refreshHost"
  />
</div>
</template>

<script>
import http from '@/utils/networking'
import {golive as apis} from '@/constants/api'
import {TASK_TYPE, TASKS} from '@/constants/enum'
import SearchSelect from '@/components/global/SearchSelect'
import ExecResult from '@/components/global/Exec'

let poll = null

export default {
  components: {
    SearchSelect,
    ExecResult
  },

  data () {
    return {
      plan: {
        id: '',
        name: '',
        golive_expected_time: '',
        notes: '',
        stages: [],
        execution_info_types: [],
        status: {
          value: ''
        }
      },
      currStageIdx: '',
      showResult: false,
      execResultId: '',

      TASK_TYPE: {...TASK_TYPE}
    }
  },

  created () {
    let id = this.id = this.$route.params.id

    http.doGet(apis.execPlan, {id}).then(({data}) => {
      this.plan = data
      // 解构
      this.plan.stages.map((x, idx) => {
        let _data = Object.assign({isshow: false}, x)
        let _arr = []
        x.commit_ids.map(c => {
          _arr.push({id: c.commit_id, text: c.text})
        })
        _data.commit_ids = _arr
        this.plan.stages.splice(idx, 1, _data)
      })
    })
  },

  methods: {
    onShowCodeBack(idx) {
      this.plan.stages[idx].isshow = !this.plan.stages[idx].isshow
    },
    onSelectCommit(idx, commit) {
      this.plan.stages[idx].commit_id = commit.id
      this.plan.stages[idx].commit_text = commit.text
      let _data = Object.assign({}, this.plan.stages[idx])
      this.plan.stages.splice(idx, 1, _data)
    },
    onCommitSave(idx) {
      let _data = this.plan.stages[idx]
      let _id = _data.input_id || _data.commit_id
      http.doPost(apis.stageRollback, {id: _data.id}, {commit_id: _id}).then((data) => {
        // 查询回滚状态
        this.onRollbackExec(data.data.execution_id)
      })
    },
    onRollbackExec (execId) {
      http.doGet(apis.execResult, {id: execId}).then(({data}) => {
        this.showResult = true
        this.execResultId = execId
      })
    },
    onExec (sidx, execId) {
      this.currStageIdx = sidx
      let stageId = this.plan.stages[sidx].id

      http.doPost(apis.run, {stageId, execId}).then(({data}) => {
        this.showResult = true
        this.execResultId = data.execution_id
      })
    },

    onExecAll (type) {
      this.currStageIdx = ''

      http.doPost(apis.runAll, {planId: this.id, type}).then(({data}) => {
        this.showResult = true
        this.execResultId = data.execution_id
      })
    },

    onReleaseDone() {
      let fetch = http.doPost(apis.releaseDone, {planId: this.id})

      fetch.then(({data}) => {
        this.$store.dispatch('createAlert', {type: 'info', message: '保存成功'})
        setTimeout(() => { this.$router.push({name: 'plan_list'}) }, 2 * 1000)
      }, msg => {
        this.$store.dispatch('createAlert', {type: 'warning', message: msg})
      })
    },

    refreshHost () {
      if (this.currStageIdx !== '') {
        let stage = this.plan.stages[this.currStageIdx]

        http.doGet(apis.stageHosts, {id: stage.id}).then(({data}) => {
          stage.hosts = data.list
        })
      } else {
        window.location.reload()
      }
    },

    getTaskById: getTaskById
  },

  filters: {
    idToName (id) {
      return getTaskById(id).text
    },

    toValue (t) {
      let taskData = getTaskById(t.function_id)
      let once = t.params && t.params.run_once ? ' (只执行一次)' : ''
      return t.params[taskData.param] + once
    },

    statusToText (status) {
      return status ? '成功' : '失败'
    }
  }
}

let taskMap = TASKS.reduce((acc, x) => {
  acc[x.id] = x
  return acc
}, {})

function getTaskById(id) {
  return taskMap[id]
}
</script>

<style lang="less" scoped>
ul,
li {
  margin: 0;
  padding: 0;
  list-style: none;
}
.list-item {
  padding: 6px 0;
  span:first-child {
    display: inline-block;
    width: 150px;
  }
}

.stage {
  display: flex;
}
.stage-info {
  flex: 1;
}
.stage-op {
  width: 250px;
  margin-left: 20px;
  padding: 0 20px;
}
.op-logs {
  height: 260px;
  margin-bottom: 20px;
  overflow: auto;
  li {
    margin-bottom: 8px;
  }
  span:first-child {
    margin-right: 5px;
  }
}
.op-ops {
  button {
    margin-bottom: 10px;
  }
}

.op-all {
  margin: 50px 0;
  button {
    width: 120px;
    margin-left: 20px;
  }
}

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
.rollback-title {
  padding: 60px 0 15px 0;
  color: #c3c3c3;
  cursor: pointer;
  user-select: none;
}
.rollback-box {
  width: 50%;
  .back-list {
    margin-bottom: 15px;
  }
}
</style>
