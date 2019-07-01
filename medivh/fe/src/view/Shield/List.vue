<template>
  <div class="box box-primary">
    <div class="box-header with-border">
      <h3 class="box-title">列表</h3>
      <div class="box-tools">
        <button type="button" class="btn btn-info" @click="showAddIp()">
          添加IP到黑名单
        </button>
      </div>
    </div>
    <table-box :url="url" :reloadData.sync="reloadData">
      <tr slot="ths">
        <th>Ip</th>
        <th>ExtraData</th>
        <th>操作</th>
      </tr>
      <template slot="item" scope="props">
        <tr>
          <td>
            {{ props.item.ip }}
          </td>
          <td>
            {{ props.item.extra_data }}
          </td>
          <td>
            <button type="button" class="btn btn-danger" @click="delIp(props.item.ip)">
              删除
            </button>
          </td>
        </tr>
      </template>
    </table-box>
    <confirm-modal :show.sync="showModal" @ok="addIp">
        <span slot="header">
          添加Ip到黑名单
        </span>
      <span slot="body">
          IP：<input type="text" v-model="currentIp" name="current_ip" class="form-control"/>
        </span>
    </confirm-modal>
  </div>
</template>

<script>
  import { shield as API } from '@/constants/api'
  import TableBox from '@/components/global/TableBox'
  import NetWorking from '@/utils/networking'
  import ConfirmModal from '@/components/global/ConfirmModal'

  export default {
    components: {TableBox, ConfirmModal},

    data () {
      return {
        url: API.blackips,
        showModal: false,
        currentIp: null,
        reloadData: false
      }
    },

    methods: {
      showAddIp () {
        this.showModal = true
      },

      addIp () {
        NetWorking
          .doPost(API.ipAdd, {ip: this.currentIp})
          .then(() => {
            this.reloadData = true
          })
      },

      delIp (ip) {
        NetWorking
          .doPost(API.ipDel, {ip: ip})
          .then(() => {
            this.reloadData = true
          })
      }
    }
  }
</script>
