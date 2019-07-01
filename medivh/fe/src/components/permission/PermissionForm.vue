<template>
  <div>
    <div class="form-group">
      <label for="name">权限组名</label>
      <input class="form-control" id="name" name="name" v-model="group.name"/>
    </div>
    <div class="form-group">
      <label for="user">用户</label>
      <v-select multiple :options="users" :value.sync="selectedUsers" id="user">
      </v-select>
    </div>
    <div class="form-group">
      <label for="permission">权限</label>
      <v-select multiple :options="permissions" :value.sync="selectedPermissions" id="permission">
      </v-select>
    </div>
    <div class="form-group">
      <label for="permission">服务</label>
      <v-select multiple :options="services" :value.sync="selectedServices" id="services">
      </v-select>
    </div>
  </div>
</template>

<script>
  import VSelect from 'vue-select'
  import { permission as API, cmdb as API2, golive as goliveApi } from '@/constants/api'
  import NetWorking from '@/utils/networking'

  export default {
    components: {VSelect},
    props: ['group'],

    data () {
      return {
        users: [],
        permissions: [],
        services: [],
        selectedUsers: [],
        selectedPermissions: [],
        selectedServices: []
      }
    },

    watch: {
      group (group) {
        if (group !== null) {
          this.selectedUsers = this.buildUsers(group.users)
          this.selectedPermissions = this.buildPermissions(group.permissions)
          this.selectedServices = this.buildServices(group.services)
        }
      },

      selectedUsers (users) {
        this.$emit('usersUpdated', users)
      },

      selectedPermissions (permissions) {
        this.$emit('permissionsUpdated', permissions)
      },

      selectedServices (services) {
        this.$emit('servicesUpdated', services)
      }
    },

    created () {
      this.fetchUsers()
      this.fetchPermissions()
      this.fetchServices()
    },

    methods: {
      fetchUsers () {
        NetWorking
          .doGet(API2.users, {all: 1})
          .then((response) => {
            this.users = this.buildUsers(response.data.list)
          })
      },

      fetchPermissions () {
        NetWorking
          .doGet(API.list)
          .then((response) => {
            this.permissions = this.buildPermissions(response.data.list)
          })
      },

      fetchServices () {
        NetWorking
          .doGet(API2.services)
          .then((response) => {
            this.services = this.buildServices(response.data.list)
          })
      },

      buildUsers (users) {
        return users.map((user) => {
          return {label: user.name, value: user.id}
        })
      },

      buildPermissions (permissions) {
        return permissions.map((permission) => {
          return {label: permission.code, value: permission.id}
        })
      },

      buildServices (services) {
        return services.map((service) => {
          return {label: service.name, value: service.id}
        })
      }
    }
  }
</script>
