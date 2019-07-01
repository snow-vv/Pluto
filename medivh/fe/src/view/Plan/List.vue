<template>
  <div class="box box-primary">
    <div class="box-header with-border">
      <h3 class="box-title">列表</h3>
      <div class="box-tools">
        <router-link class="btn btn-block btn-primary btn-sm" :to="{ name: 'plan_new'}">
          新申请
        </router-link>
      </div>
    </div>
    <table-box :url="url">
      <tr slot="ths">
        <th>申请ID</th>
        <th>申请描述</th>
        <th>期望上线时间</th>
        <th>状态</th>
        <th>申请人</th>
        <th>服务</th>
        <th>备注</th>
        <th style="width:200px">操作</th>
      </tr>
      <template slot="item" scope="props">
        <tr>
          <td>
            {{ props.item.id }}
          </td>
          <td>
            {{ props.item.description }}
          </td>
          <td>
            {{ props.item.golive_expected_time | date(true) }}
          </td>
          <td>
            <span class="label" :class="getStatusText(props.item.status)">{{ props.item.status.desc }}</span>
          </td>
          <td>
            {{ props.item.creator.name }}
          </td>
          <td>
            <div class="label label-default" v-for="(service, idx) in props.item.services" style="display:inline-block">{{ service.name }}</div>
          </td>
          <td>
            {{ props.item.notes }}
          </td>
          <td>
            <button type="button" class="btn btn-info" @click="checkDetail(props.item.id)">
              查看详情
            </button>
            <button type="button" class="btn btn-info" @click="goExecute(props.item.id)"
                    v-show="canExecute(props.item.status)">
              执行
            </button>
          </td>
        </tr>
      </template>
    </table-box>
  </div>
</template>

<script>
  import {golive as API} from '@/constants/api'
  import TableBox from '@/components/global/TableBox'
  import {PLAN_STATUS} from '@/constants/enum'
  import {mapGetters} from 'vuex'

  export default {
    components: {TableBox},

    computed: {
      ...mapGetters({
        currentUser: 'currentUser'
      })
    },

    data () {
      return {
        type: '',
        url: API.plans
      }
    },

    methods: {
      checkDetail (id) {
        this.$router.push({name: 'plan_edit', params: {id: id}})
      },

      canExecute (status) {
        return status.value !== 1
      },

      goExecute (id) {
        this.$router.push({name: 'execution', params: {id: id}})
      },

      getStatusText (status) {
        switch (status.value) {
          case PLAN_STATUS.FAILED: {
            return 'bg-red'
          }
          case PLAN_STATUS.GOLIVED: {
            return 'bg-green'
          }
          case PLAN_STATUS.GOLIVING: {
            return 'bg-yellow'
          }
          case PLAN_STATUS.AUDIT_PASS: {
            return 'label-primary'
          }
          case PLAN_STATUS.EDITING: {
            return 'bg-blue'
          }
        }
      }
    }
  }
</script>

<style scoped>
  img.avatar, div.avatar {
    border-radius: 50%;
    width: 35px;
    height: 35px;
    line-height: 35px;
  }

  div.avatar {
    background-color: #FFEBEE;
    color: #555;
    font-size: 16px;
    margin-right: 10px;
    text-align: center;
    vertical-align: top;
  }
</style>
