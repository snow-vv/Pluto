<template>
  <div class="box box-solid col-md-8 col-md-offset-2" style="background-color: #ecf0f5;box-shadow:none">
    <LoadingOverlay v-show="showOverlay"></LoadingOverlay>
    <div class="row">
      <div class="col-md-8" v-for="grey in greys">
        <div class="box box-primary">
          <div class="box-header with-border">
            <h3 class="box-title">{{ grey.name }}</h3>
          </div>
          <div class="box-body">
            <strong><i class="fa fa-map-marker margin-r-5"></i> 路由表 地址</strong>
            <p class="text-muted">{{ grey.route_path }}</p>
            <hr>
            <strong><i class="fa fa-info-circle margin-r-5"></i> 状态</strong>
            <p class="text-muted">
              <span class="label" :class="statusClass(grey.status)">{{ grey.status.desc }}</span>
            </p>
            <hr>
            <div v-if="canExecute(grey.status)">
              <strong><i class="fa fa-pencil margin-r-5"></i> 服务</strong>
              <p>
                <div v-for="service in services">
                  <template class="checkbox-wrap" v-if="canGrey(service.name)">
                    <input type="checkbox" :id="service.name" :value="service.id" v-model="selectedServices">
                    <label :for="service.name">{{service.name}}</label>
                  </template>
                </div>
              <hr>
            </div>
            <div v-if="ExecutedSucccess(grey.status)">
              <strong><i class="fa fa-file-text-o margin-r-5"></i> 成功执行了以下操作 </strong>
              <pre>{{ grey.description }}</pre>
              <hr>
            </div>
            <button class="btn btn-primary" @click="confirmGrey(grey.id)" v-if="canExecute(grey.status)">
              执行
            </button>

            <button class="btn btn-info" @click="confirmReset(grey.id)" v-if="!canExecute(grey.status)">
              重置
            </button>
            <confirm-modal :show.sync="showModal" @ok="executeGrey(grey.id)">
              <span slot="header">
                将要执行以下操作，是否继续？
              </span>
              <span slot="body">
                <pre>{{note}}</pre>
              </span>
            </confirm-modal>
            <confirm-modal :show.sync="showResetModal" @ok="resetGrey(grey.id)">
              <span slot="header">
                将会执行下列操作，是否重置？
              </span>
              <span slot="body">
                <pre>{{resetNote}}</pre>
              </span>
            </confirm-modal>
          </div>
        </div>
      </div>
    </div>
    <exec-result :visible.sync="showResult"
                 :id="execResultId"
                 @close="refreshHost">
    </exec-result>
  </div>
</template>

<script>
  import {golive as API} from '@/constants/api'
  import {GREY_STATUS, SERVICE_GREY_IN_OLD_WAY} from '@/constants/enum'
  import NetWorking from '@/utils/networking'
  import TableBox from '@/components/global/TableBox'
  import ConfirmModal from '@/components/global/ConfirmModal'
  import LoadingOverlay from '@/components/global/LoadingOverlay'
  import ExecResult from '@/components/global/Exec'

  export default {
    components: {TableBox, ConfirmModal, LoadingOverlay, ExecResult},

    data () {
      return {
        greys: [],
        services: [],
        selectedServices: [],
        showOverlay: false,
        disableAllBtn: false,
        showResult: false,
        execResultId: null,
        note: '',
        resetNote: '',
        showModal: false,
        showResetModal: false
      }
    },

    created () {
      this.fetchData()
    },

    methods: {
      fetchData () {
        this.showLoading()
        NetWorking
          .doGet(API.greys)
          .then((response) => {
            this.greys = response.data.list
            this.hideLoading()
            this.checkStatus()
          }, () => {
            this.hideLoading()
          })
        NetWorking
          .doGet(API.grey_services)
          .then((response) => {
            this.services = response.data.list
            this.hideLoading()
            this.checkStatus()
          }, () => {
            this.hideLoading()
          })
      },

      // 判断能否通过老的灰度方式进行灰度
      canGrey (service_name) {
        return SERVICE_GREY_IN_OLD_WAY.includes(service_name)
      },

      confirmGrey (id) {
        NetWorking
          .doPost(API.confirmGrey, {id: id}, {services: this.selectedServices})
          .then((response) => {
            this.note = response.data.description
            this.showModal = true
          })
      },

      executeGrey (id) {
        this._doAction(id, API.greyStart)
      },

      confirmReset (id) {
        NetWorking
          .doPost(API.confirmReset, {id: id})
          .then((response) => {
            this.resetNote = response.data.description
            this.showResetModal = true
          })
      },

      resetGrey (id) {
        this._doAction(id, API.greyReset)
      },

      _doAction (id, url) {
//        this.showLoading()
        NetWorking
          .doPost(url, {id: id}, {services: this.selectedServices})
          .then((response) => {
            this.execResultId = response.data.execution_id
            this.showResult = true
            this.hideLoading()
          }, () => {
            this.hideLoading()
          })
      },

      /**
       * 检查Grey列表中的状态
       */
      checkStatus () {
        this.greys.forEach((grey) => {
          // 如果有任何一个灰度的状态是非正常，则所有按钮处于不可点击状态
          if (grey.status.value !== GREY_STATUS.NORMAL) {
            this.disableAllBtn = true
            return false
          }
        })
      },

      statusClass (status) {
        switch (status.value) {
          case GREY_STATUS.NORMAL:
            return 'label-primary'
          case GREY_STATUS.PROCESSING:
            return 'bg-blue'
          case GREY_STATUS.SUCCESS:
            return 'bg-green'
          case GREY_STATUS.RESETTING:
            return 'bg-red'
          case GREY_STATUS.FAIL:
            return 'bg-red'
          case GREY_STATUS.RESET_FAIL:
            return 'bg-red'
          default:
            return 'label-primary'
        }
      },

      canExecute(status) {
        switch (status.value) {
          case GREY_STATUS.NORMAL:
          case GREY_STATUS.FAIL:
            return true
          default:
            return false
        }
      },

      ExecutedSucccess(status) {
        if (status.value === GREY_STATUS.SUCCESS) {
          return true
        }
        return false
      },

      disableExecuteBtn (status) {
        switch (status.value) {
          case GREY_STATUS.NORMAL:
            return this.disableAllBtn || false
          case GREY_STATUS.FAIL:
            return false
          default:
            return true
        }
      },

      disableResetBtn (status) {
        switch (status.value) {
          case GREY_STATUS.FAIL:
          case GREY_STATUS.SUCCESS:
          case GREY_STATUS.RESET_FAIL:
            return false
          default:
            return true
        }
      },

      refreshHost () {
        window.location.reload()
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
<style scoped>
  pre {
    display: block;
    padding: 9.5px;
    margin: 0 0 10px;
    font-size: 13px;
    line-height: 1.42857143;
    color: #333;
    word-break: break-all;
    word-wrap: break-word;
    background-color: #f5f5f5;
    border: none;
    border-radius: 0
  }

  .checkbox-wrap {
    width: 90%;
    position: relative;
    margin: 0 auto;
    top: 30%;
    height: 40%;
    background-color: white;
  }

  input[type="checkbox"] {
    /* width: 40px; */
    /* height: 40px; */
    /* -webkit-border-radius: 50%; */
    display: none;
  }

  input[type="checkbox"] + label {
    display: inline-block;
    width: 20%;
    margin-top: 10px;
    margin-left: 5px;
    text-align: left;
    -webkit-box-sizing: border-box;
  }

  label::before {
    content: "";
    display: inline-block;
    width: 30px;
    height: 30px;
    background: #EEE;
    vertical-align: middle;
    -webkit-border-radius: 50%;
    margin-right: 5px;
    -webkit-box-sizing: border-box;
    -webkit-transition: background ease-in .5s
  }

  input[type="checkbox"]:checked + label::before {
    background-color: rgb(53, 183, 111);
    border: 5px #EEEEEE solid;
  }
</style>
