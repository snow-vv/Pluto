<template>
<div class="login-box">
  <div class="login-box-body box-body">
    <form
      method="post"
      @submit.prevent="onSubmit">
      <div class="box-body">
        <div class="form-group has-feedback">
          <input
            type="password"
            class="form-control"
            placeholder="请输入旧密码"
            v-model.trim="oldPsw"
          />
          <span class="glyphicon glyphicon-lock form-control-feedback"></span>
        </div>

        <div class="form-group has-feedback">
          <input
            type="password"
            class="form-control"
            placeholder="请输入新密码"
            v-model.trim="newPsw"
          />
          <span class="glyphicon glyphicon-lock form-control-feedback"></span>
        </div>

        <div class="form-group has-feedback">
          <input
            type="password"
            class="form-control"
            placeholder="请再次输入新密码"
            v-model.trim="newPsw2"
          />
          <span class="glyphicon glyphicon-lock form-control-feedback"></span>
        </div>

        <div class="row">
          <div class="col-xs-12">
            <input
              class="btn btn-primary btn-block btn-flat"
              value="确认修改"
              type="submit"
              :disabled="disabled">
          </div>
        </div>
      </div>
    </form>
  </div>
</div>
</template>

<script>
import http from '@/utils/networking'
import * as apis from '@/constants/api'

export default {
  data () {
    return {
      oldPsw: '',
      newPsw: '',
      newPsw2: '',
      disabled: false
    }
  },

  methods: {
    onSubmit () {
      if (!this.oldPsw || !this.newPsw || !this.newPsw2) {
        this.$store.dispatch('createAlert', {type: 'warning', message: '请输入密码'})
        return
      }

      if (this.newPsw !== this.newPsw2) {
        this.$store.dispatch('createAlert', {type: 'warning', message: '两次密码不一致'})
        return
      }

      this.disabled = true

      let data = {
        password: this.oldPsw,
        new_password: this.newPsw
      }

      http.doPost(apis.accounts.psw, null, data).then(() => {
        this.$store.dispatch('createAlert', {type: 'info', message: '修改成功'})
      }, (message) => {
        this.disabled = false
        this.$store.dispatch('createAlert', {type: 'warning', message})
      })
    }
  }
}
</script>
