<template>
  <loading-box :showOverlay="showOverlay">
    <span slot="title">编辑权限</span>
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
  import { permission as API } from '@/constants/api'
  import NetWorking from '@/utils/networking'

  export default {
    components: {LoadingBox, PermissionForm},

    data () {
      return {
        id: '',
        group: {},
        showOverlay: false
      }
    },

    created () {
      this.id = this.$route.params.id
      this.fetchData()
    },

    methods: {
      fetchData () {
        this.showLoading()
        NetWorking
          .doGet(API.group, {id: this.id})
          .then((response) => {
            this.group = response.data
            this.hideLoading()
          }, () => {
            this.hideLoading()
          })
      },

      permissionsUpdated (permissions) {
        this.group.permissions = permissions.map((permission) => {
          return {name: permission.label, id: permission.value}
        })
      },

      servicesUpdated (services) {
        this.group.services = services.map((service) => {
          return {name: service.label, id: service.value}
        })
      },

      usersUpdated (users) {
        this.group.users = users.map((user) => {
          return {name: user.label, id: user.value}
        })
      },

      saveGroup () {
        this.showLoading()
        NetWorking
          .doPost(API.group, {id: this.id}, {data: this.group})
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
