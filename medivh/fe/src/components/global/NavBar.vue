<!--顶部导航栏-->
<template>
  <header class="main-header">
    <a class="logo" href="/">
    <span class="logo-lg">
      <b>Medivh</b>
    </span>
    </a>
    <nav class="navbar navbar-static-top" role="navigation">
      <a class="sidebar-toggle" data-toggle="offcanvas" role="button">
        <span class="sr-only">Toggle navigation</span>
      </a>
      <div class="navbar-custom-menu">
        <ul class="nav navbar-nav navbar-right" style="margin-right:0">
          <li class="dropdown user user-menu">
            <a aria-expanded="false" class="dropdown-toggle" data-toggle="dropdown" href="#">
              <img alt="User Image" class="user-image" :src="currentUser.avatar_url">
              <span class="hidden-xs">{{ currentUser.name }}</span>
            </a>
            <ul class="dropdown-menu">
              <li class="user-header">
                <img alt="User Image" class="img-circle"
                     :src="currentUser.avatar_url">
                <p>
                  {{ currentUser.name }} - {{ currentUser.username }}
                  <small>{{ currentUser.created_at }}</small>
                </p>
              </li>
              <li class="user-footer">
                <div>
                  <router-link
                    class="btn btn-default btn-flat"
                    :to="{name: 'password'}">修改密码</router-link>
                  <a
                    class="btn btn-default btn-flat pull-right"
                    href="javascript:;"
                    @click="signOut()">Sign Out</a>
                </div>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script>
  import NetWorking from '@/utils/networking'
  import * as API from '@/constants/api'
  import { mapGetters } from 'vuex'

  export default {

    computed: {
      ...mapGetters({
        currentUser: 'currentUser'
      })
    },

    methods: {
      signOut: function () {
        NetWorking
          .doGet(API.accounts.logout, null, null)
          .then(() => {
            this.$store.dispatch('deleteUser')
            this.$router.replace({name: 'login'})
          })
      }
    }
  }
</script>
