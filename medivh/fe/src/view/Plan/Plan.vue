<template>
  <div class="plan">
    <form class="form-horizontal clearfix">
      <div class="box box-solid">
        <div class="box-body">
          <div class="form-group">
            <label class="form-name control-label">描述</label>
            <div class="form-value">
              <input
                  class="form-control"
                  :disabled="disabled"
                  v-model="plan.name">
            </div>
          </div>

          <div class="form-group">
            <label class="form-name control-label">期望上线时间</label>
            <div class="form-value">
              <date-picker
                  :disabled="disabled"
                  :value="plan.golive_expected_time"
                  @input="onDate"
                  format="YYYY-MM-DD HH:mm:ss"
                  time
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-name control-label">备注</label>
            <div class="form-value">
            <textarea
                class="form-control"
                :disabled="disabled"
                v-model="plan.notes"></textarea>
            </div>
          </div>
        </div>
      </div>

      <div
          v-for="(s, idx) in plan.stages"
          class="box stage">
        <div class="box-body">
          <div class="form-group">
            <label class="form-name control-label">服务</label>
            <div class="form-value">
              <search-select
                  :disabled="disabled"
                  :data="services"
                  :current="s.service_id"
                  @select="service => onSelectService(idx, service)"
              />
            </div>
          </div>

          <div v-for="(t, tidx) in s.tasks" class="form-group task">
            <label class="form-name control-label">{{t.text}}</label>

            <div class="form-value">
              <div v-if="t.type==TASK_TYPE.INPUT">
                <input
                    class="form-control"
                    v-model="t.value"
                    :disabled="disabled"
                    :placeholder="t.place">
                <label
                    v-if="t.once"
                    class="exec-once">
                  <input
                      type="checkbox"
                      v-model="t.onceValue">只执行一次</label>
              </div>
              <i v-else class="fa fa-check"></i>
            </div>

            <div v-if="!disabled" class="form-op">
              <button
                  v-if="tidx!=0"
                  type="button"
                  class="btn btn-default add"
                  @click="onMoveUpTask(idx, tidx)"
              >上移
              </button>
              <button
                  type="button"
                  class="btn btn-default add"
                  @click="onDelTask(idx, tidx)"
              >删除
              </button>
            </div>
          </div>

          <div v-if="!disabled" class="form-group">
            <label class="form-name control-label"></label>
            <div class="form-value">
              <dropdown
                  class="add-task"
                  :options="tasks"
                  @select="task => onAddTask(idx, task)">添加任务
              </dropdown>
            </div>
          </div>
        </div>

        <div v-if="!disabled" class="box-footer clearfix">
          <div class="pull-right">
            <button
                v-if="plan.stages.length>1"
                type="button"
                class="btn btn-danger add"
                @click="onDelStage(idx)"
            >删除
            </button>
            <button
                v-if="idx!=0"
                type="button"
                class="btn btn-default add"
                @click="onMoveUpStage(idx)"
            >上移
            </button>
            <button
                v-if="idx==plan.stages.length-1"
                type="button"
                class="btn btn-default add"
                @click="onAddStage"
            >添加服务
            </button>
          </div>
        </div>
      </div>

      <div v-if="!disabled" class="save-ops pull-right">
        <button type="button" class="btn btn-info save" @click.once="onSave(false)">保存</button>
        <button type="button" class="btn btn-primary" @click.once="onSave(true)">保存并提交</button>
      </div>
    </form>
  </div>
</template>

<script>
  import SearchSelect from '@/components/global/SearchSelect'
  import Dropdown from '@/components/global/Dropdown'
  import DatePicker from '@/components/global/DatePicker'
  import http from '@/utils/networking'
  import {golive as apis} from '@/constants/api'
  import {TASK_TYPE, TASKS, PLAN_STATUS} from '@/constants/enum'

  let taskMap = TASKS.reduce((acc, x) => {
    acc[x.id] = x
    return acc
  }, {})

  const createStage = () => {
    return {
      service_id: '',
      tasks: []
    }
  }

  export default {
    components: {
      SearchSelect,
      Dropdown,
      DatePicker
    },

    data() {
      return {
        plan: {
          id: '',
          name: '',
          golive_expected_time: '',
          notes: '',
          stages: [
            createStage()
          ],
          status: {
            value: ''
          }
        },

        services: [],
        iscommit: false,
        commit_id: '',
        commit_text: '',
        input_id: '',
        commits: [],
        tasks: TASKS.map(x => ({...x})),
        TASK_TYPE: {...TASK_TYPE}
      }
    },

    computed: {
      disabled() {
        let status = this.plan.status.value
        return status !== '' && status !== PLAN_STATUS.EDITING
      }
    },

    created() {
      let id = this.id = this.$route.params.id
      if (id) {
        this.fetchPlan(id)
      }
      this.fetchServices()
    },

    methods: {
      fetchPlan(id) {
        http.doGet(apis.plan, {id}).then(({data}) => {
          this.plan = this.transformIn(data)
        })
      },

      fetchServices() {
        http.doGet(apis.services).then(({data}) => {
          this.services = data.list.map(x => ({id: x.id, text: x.name}))
        })
      },

      transformIn(data) {
        data.golive_expected_time *= 1000

        if (data.stages.length > 0) {
          data.stages.forEach(stage => {
            stage.tasks = stage.tasks.map(task => {
              let taskData = this.getTaskById(task.function_id)
              return {
                id: task.id,
                function_id: task.function_id,
                text: taskData.text,
                value: !taskData.param ? '' : task.params[taskData.param],
                type: taskData.type,
                place: taskData.place || '',
                once: taskData.once,
                onceValue: task.params.run_once || false
              }
            })
          })
        } else {
          data.stages.push(createStage())
        }

        return data
      },

      onDate(str, time) {
        this.plan.golive_expected_time = time
      },

      getTaskById(id) {
        return taskMap[id]
      },

      onAddStage() {
        this.plan.stages.push(createStage())
      },
      onDelStage(idx) {
        this.plan.stages.splice(idx, 1)
      },
      onMoveUpStage(idx) {
        let stages = this.plan.stages
        let stage = stages[idx - 1]
        this.$set(stages, idx - 1, stages[idx])
        this.$set(stages, idx, stage)
      },

      onSelectService(idx, service) {
        this.plan.stages[idx].service_id = service.id
      },

      onAddTask(idx, task) {
        this.plan.stages[idx].tasks.push({
          function_id: task.id,
          text: task.text,
          value: '',
          place: task.place,
          type: task.type,
          once: task.once,
          onceValue: true
        })
      },
      onDelTask(idx, tidx) {
        this.plan.stages[idx].tasks.splice(tidx, 1)
      },
      onMoveUpTask(idx, tidx) {
        let tasks = this.plan.stages[idx].tasks
        let task = tasks[tidx - 1]
        this.$set(tasks, tidx - 1, tasks[tidx])
        this.$set(tasks, tidx, task)
      },

      transformOut() {
        let stages = this.plan.stages.map(stage => {
          return {
            ...stage,
            tasks: stage.tasks.map(task => {
              let taskData = this.getTaskById(task.function_id)
              let ret = {
                id: task.id,
                run_once: task.once,
                function_id: task.function_id
              }
              if (taskData.param) {
                ret[taskData.param] = task.value
              }
              if (taskData.once) {
                ret.run_once = task.onceValue
              }
              return ret
            })
          }
        })
        return {
          ...this.plan,
          golive_expected_time: Math.floor(this.plan.golive_expected_time / 1000),
          stages: stages
        }
      },

      onSave(submit) {
        let plan_data = this.transformOut()
        let params = {
          is_audit: !!submit,
          data: JSON.stringify(plan_data)
        }
        // // 拉代码task必须指定commit SHA
        // let stages = plan_data.stages
        // for (var stage of stages) {
        //   for (var task of stage.tasks) {
        //     if (task.function_id === 1 && task.version === '') {
        //       this.$store.dispatch('createAlert', {type: 'warning', message: '拉代码必须指定commit SHA'})
        //       return setTimeout(() => { window.location.reload() }, 2 * 1000)
        //     }
        //   }
        // }
        let fetch = this.id
          ? http.doPost(apis.plan, {id: this.id}, params)
          : http.doPost(apis.createPlan, null, params)

        fetch.then(({data}) => {
          this.$store.dispatch('createAlert', {type: 'info', message: '保存成功'})
          setTimeout(() => {
            this.$router.push({name: 'plan_list'})
          }, 2 * 1000)
        }, msg => {
          this.$store.dispatch('createAlert', {type: 'warning', message: msg})
        })
      }
    }
  }
</script>

<style lang="less" scoped>
  .form-group {
    display: flex;
    margin: 15px 0;

    .form-name {
      width: 150px;
      margin-right: 20px;
    }
    .form-value {
      flex: 1;
    }
    .form-op {
      margin-left: 20px;
      width: 150px;
    }
  }

  .exec-once {
    margin-top: 8px;
    font-weight: 400;
    user-select: none;
    cursor: pointer;
    input {
      margin-right: 5px;
    }
  }

  button {
    width: 120px;
  }

  .stage {
    button {
      margin-left: 10px;
      &:first-child {
        margin-left: 0;
      }
    }
  }

  .task {
    button {
      width: 60px;
    }
  }

  .add-task {
    width: 120px;
  }

  .save-ops {
    margin: 30px 0;
  }

  .save {
    margin-right: 20px;
  }

  .flex-box {
    display: flex;
    display: -webkit-flex;
    .flex-item {
      flex: 1;
      width: 50%;
    }
    .flex-item:last-child {
      margin-left: 20px;
    }
  }
</style>
