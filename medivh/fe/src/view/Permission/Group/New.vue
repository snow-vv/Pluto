<template>
  <loading-box :showOverlay="showOverlay">
    <span slot="title">新增权限组</span>
    <div slot="body">
      <form accept-charset="UTF-8" method="post">
        <permission-form :group="group"
                         @usersUpdated="usersUpdated"
                         @permissionsUpdated="permissionsUpdated"
                         @servicesUpdated="servicesUpdated"
        ></permission-form>
      </form>
    </div>
    <div slot="footer">
      <button type="button" class="btn btn-primary" @click="saveGroup">
        保存
      </button>
    </div>
  </loading-box>
</template>

<script>
  import LoadingBox from '@/components/global/LoadingBox'
  import PermissionForm from '@/components/permission/PermissionForm'
  import {permission as API} from '@/constants/api'
  import NetWorking from '@/utils/networking'

  export default {
    components: {LoadingBox, PermissionForm},

    data () {
      return {
        group: {},
        showOverlay: false
      }
    },

    methods: {

      permissionsUpdated (permissions) {
        this.group.permissions = permissions.map((permission) => {
          return {name: permission.label, id: permission.value}
        })
      },

      usersUpdated (users) {
        this.group.users = users.map((user) => {
          return {name: user.label, id: user.value}
        })
      },

      servicesUpdated (services) {
        this.group.services = services.map((service) => {
          return {name: service.label, id: service.value}
        })
      },

      saveGroup () {
        this.showLoading()
        NetWorking
          .doPost(API.newGroup, null, {data: this.group})
          .then(() => {
            this.$router.replace({name: 'permission_group_list'})
            this.hideLoading()
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
