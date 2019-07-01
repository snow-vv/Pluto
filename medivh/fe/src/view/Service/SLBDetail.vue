<template>
  <div class="row">
    <div class="col-md-3">
      <div class="box box-primary">
        <div class="box-header with-border">
          <h3 class="box-title">SLB信息</h3>
        </div>
        <div class="box-body">
          <strong><i class="fa fa-book margin-r-5"></i>名称</strong>
          <p class="text-muted">
            {{ slb.name }}
          </p>
          <hr>
          <strong><i class="fa fa-file-text-o margin-r-5"></i> 描述</strong>
          <p class="text-muted">{{ slb.description }}</p>
        </div>
      </div>
    </div>
    <div class="col-md-9">
      <div class="box box-primary">
        <div class="box-header with-border">
          <h3 class="box-title">ECS列表</h3>
        </div>
        <table-box :url="url" :pathParams="pathParams" @afterFetchData="afterFetchData" :reloadData="reloadData">
          <tr slot="ths">
            <th>ID</th>
            <th>名称</th>
            <th>权重</th>
            <th style="width:200px">操作</th>
          </tr>
          <template slot="item" scope="props">
            <tr>
              <td>
                {{ props.item.id }}
              </td>
              <td>
                {{ props.item.name }}
              </td>
              <td>
                {{ props.item.weight }}
              </td>
              <td>
                <button type="button" class="btn btn-info" @click="showEditWeight(props.item.id, props.item.weight)">
                  改权重
                </button>
              </td>
            </tr>
          </template>
        </table-box>
      </div>
      <confirm-modal :show.sync="showModal" @ok="changeWeight">
        <span slot="header">
          调整权重
        </span>
        <span slot="body">
          权重：<input type="text" v-model="currentWeight" name="current_weight" class="form-control"/>
        </span>
      </confirm-modal>
    </div>
  </div>
</template>

<script>
  import { cmdb as API } from '@/constants/api'
  import NetWorking from '@/utils/networking'
  import TableBox from '@/components/global/TableBox'
  import ConfirmModal from '@/components/global/ConfirmModal'

  export default {
    components: {TableBox, ConfirmModal},

    data () {
      return {
        slb: {},
        url: API.slb,
        pathParams: {id: this.$route.params.id},
        showModal: false,
        currentEcsId: null,
        currentWeight: null,
        reloadData: false
      }
    },

    methods: {
      afterFetchData (data) {
        this.slb = data
      },

      showEditWeight (id, weight) {
        this.currentEcsId = id
        this.currentWeight = weight
        this.showModal = true
      },

      changeWeight () {
        NetWorking
          .doPost(API.slbChangeWeight,
            {id: this.$route.params.id, ecsId: this.currentEcsId},
            {params: {weight: this.currentWeight}}
          )
          .then(() => {
            this.reloadData = true
          })
      }
    }
  }
</script>
