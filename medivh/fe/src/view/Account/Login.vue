<template>
  <div class="login-box">
    <div class="login-logo">更美运维平台</div>
    <div class="login-box-body box-body">
      <form role="form" method="post" @submit.prevent="doLogin">
        <div class="box-body">
          <div class="form-group has-feedback">
            <input type="text" name="username" class="form-control" placeholder="用户名" v-model="user.username">
            <span class="glyphicon glyphicon-envelope form-control-feedback"></span>
          </div>

          <div class="form-group has-feedback">
            <input type="password" name="password" class="form-control" placeholder="密码" v-model="user.password">
            <span class="glyphicon glyphicon-lock form-control-feedback"></span>
          </div>

          <div class="row">
            <div class="col-xs-12">
              <input class="btn btn-primary btn-block btn-flat" type="submit" :value="buttonText"
                     :disabled="buttonDisabled">
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
  import NetWorking from '@/utils/networking'
  import * as API from '@/constants/api'

  export default {

    data () {
      return {
        user: {
          username: '',
          password: ''
        },
        buttonDisabled: false,
        buttonText: '登录'
      }
    },

    created () {
    },

    methods: {

      doLogin: function () {
        this.showLoading()
        NetWorking.doPost(API.accounts.login, null, this.user, null).then(response => {
          let status = response.error
          if (status === 0) {
            let user = response.data
            this.$store.dispatch('createUser', user)
            this.$router.push({name: 'plan_list'})
          } else {
            window.alert(response.message)
          }
          this.hideLoading()
        }, (message) => {
          this.hideLoading()
          window.alert(message)
        })
      },

      showLoading: function () {
        this.buttonDisabled = true
        this.buttonText = '登录中...'
      },

      hideLoading: function () {
        this.buttonDisabled = false
        this.buttonText = '登录'
      }

    }
  }
</script>

<style lang="less" scoped>
  .login-logo {
    padding-top: 80px;
    font-size: 24px;
    background: url(../../assets/img/gm.png) 50% 0 no-repeat;
    background-size: 60px 60px;
  }

  .login-box {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    width: 850px;
    height: 560px;
    margin: auto;
    padding: 82px 245px;
    border-radius: 4px;
    background-color: hsla(0, 0%, 100%, .28);
  }

  .login-box:before {
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: -1;
    background: url(../../assets/img/login-bg.jpg) no-repeat;
    background-size: cover;
  }
</style>
