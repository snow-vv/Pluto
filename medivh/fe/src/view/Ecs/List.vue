<template>
  <div class="box box-primary">
    <LoadingOverlay v-show="showOverlay"></LoadingOverlay>
    <div class="box-header with-border">
      <h3 class="box-title">列表</h3>
      <div class="box-tools">
        <button class="btn btn-primary" @click="doSync">同步</button>
      </div>
    </div>
    <table-box :url="url" :reloadData.sync="reloadData">
      <tr slot="ths">
        <th>名称</th>
        <th>内网IP</th>
        <th>公网IP</th>
        <th>实例ID</th>
        <th>CPU</th>
        <th>内存</th>
        <th>描述</th>
        <th>创建时间</th>
      </tr>
      <template slot="item" scope="props">
        <tr>
          <td>
            {{ props.item.name }}
          </td>
          <td>
            {{ props.item.ip }}
          </td>
          <td>
            {{ props.item.public_ip }}
          </td>
          <td>
            {{ props.item.instance_id }}
          </td>
          <td>
            {{ props.item.cpu }}
          </td>
          <td>
            {{ props.item.memory }}
          </td>
          <td>
            {{ props.item.description }}
          </td>
          <td>
            {{ props.item.created_time | date(true) }}
          </td>
        </tr>
      </template>
    </table-box>
  </div>
</template>

<script>
  import { cmdb as API } from '@/constants/api'
  import NetWorking from '@/utils/networking'
  import TableBox from '@/components/global/TableBox'
  import LoadingOverlay from '@/components/global/LoadingOverlay'

  export default {
    components: {TableBox, LoadingOverlay},

    data () {
      return {
        url: API.ecses,
        showOverlay: false,
        reloadData: false
      }
    },

    methods: {
      doSync () {
        this.showLoading()
        NetWorking
          .doPost(API.ecsesSync)
          .then(() => {
            this.hideLoading()
            this.reloadData = true
          }, () => {
            this.hideLoading()
          })
      },

      showLoading () {
        this.showOverlay = true
      },

      hideLoading () {
        this.showOverlay = false
      }
    }
  }
</script>
