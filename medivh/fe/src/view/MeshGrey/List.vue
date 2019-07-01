<template>
<div>
  <div class="box">
    <div class="box-header with-border">
      <h3 class="box-title">当前路由规则</h3>
    </div>
    <div class="box-body">
      <div v-for="item in current_rule">
        {{item['prefix']}} => {{item['dst']}};
      </div>
    </div>
  </div>
  <div class="box">
    <div class="box-header with-border">
      <h3 class="box-title">预设路由规则</h3>
    </div>
      <table class="table">
        <thead>
          <tr>
          <th>模式</th>
          <th>规则配置</th>
          <th>操作</th>
        </tr>
        </thead>
        <tbody>
          <tr v-for="rule_example in rule_examples">
              <td><h4>{{rule_example['name']}}</h4></td>
              <td>{{rule_example['rule']}}</td>
              <td><button class="btn btn-primary" @click="confirm_use_pattern(rule_example['name'], rule_example['rule'])">启用该规则</button></td>
        </tr>
        </tbody>
      </table>
      <confirm-modal :show.sync="showUsePatternModal" @ok="modify_dtabs_rule()">
        <span slot="header">
          <h3>将路由规则置为**{{selected_name}}**模式</h3>
        </span>
        <span slot="body">
          <pre>{{selected_rule}}</pre>
        </span>
      </confirm-modal>
      <confirm-modal :show.sync="showModifyModal" @ok="modify_dtabs_rule()">
        <span slot="header">
          <h3>将路由规则更改为以下规则:</h3>
        </span>
        <span slot="body">
          <pre>{{selected_rule}}</pre>
        </span>
      </confirm-modal>
  </div>
  <div class="box">
    <div class="box-header with-border">
      <h3 class="box-title">自定义路由规则</h3>
    </div>
    <div class="box-body">
      <textarea class="form-control" rows="10" v-model="dtabs_rule" placeholder="编写dtabs路由规则"></textarea>
      &nbsp;
      <button class="btn btn-primary" @click="confirm_modify">确认修改</button>
    </div>
  </div>
</div>
</template>

<script>
  import {golive as API} from '@/constants/api'
  import ConfirmModal from '@/components/global/ConfirmModal'
  import NetWorking from '@/utils/networking'

  export default {
    components: {ConfirmModal},

    data () {
      return {
        dtabs_rule: '',
        current_rule: '',
        rule_examples: '',
        showModifyModal: false,
        showUsePatternModal: false,
        selected_name: '',
        selected_rule: ''
      }
    },

    created () {
      NetWorking
        .doGet(API.dtabRulesExample)
        .then((response) => {
          this.rule_examples = response.data.list
          if (response.data.success === 0) {
            this.$store.dispatch('createAlert', {type: 'warning', message: response.data.message})
          }
        })
      NetWorking
        .doGet(API.greyRule)
        .then((response) => {
          this.current_rule = response.data.list
          if (response.data.success === 0) {
            this.$store.dispatch('createAlert', {type: 'warning', message: response.data.message})
          }
        })
    },

    methods: {
      modify_dtabs_rule() {
        NetWorking
          .doPost(API.greyRule, {}, {dtabs_rule: this.selected_rule})
          .then((response) => {
            if (response.data.success === 1) {
              this.$store.dispatch('createAlert', {type: 'info', message: response.data.message})
              setTimeout(() => { window.location.reload() }, 2 * 1000)
            } else {
              this.$store.dispatch('createAlert', {type: 'warning', message: response.data.message})
            }
          })
      },

      confirm_use_pattern(name, rule) {
        this.selected_name = name
        this.selected_rule = rule
        this.showUsePatternModal = true
      },

      confirm_modify() {
        this.selected_rule = this.dtabs_rule
        this.showModifyModal = true
      }

    }
  }
</script>
