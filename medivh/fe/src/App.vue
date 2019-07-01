<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
  import Vue from 'vue'
  import 'bootstrap/dist/css/bootstrap.css'
  import 'bootstrap/dist/js/bootstrap'
  import 'font-awesome/css/font-awesome.css'
  import 'admin-lte/dist/css/AdminLTE.css'
  import 'admin-lte/dist/css/skins/skin-blue.css'
  import 'admin-lte/dist/js/app'

  export default {
    created () {
      Vue.http.interceptors.push((request, next) => {
        next((response) => {
          this.handleResponse(response)
          return response
        })
      })
    },

    methods: {
      handleResponse (response) {
        this.$store.dispatch('deleteAlert')
        if (response.status >= 500) {
          this.handleServerError(response)
        } else {
          if (response.data.error === 401) {
            this.handleUnauthorized()
          } else if (response.data.error === 403) {
            this.handleForbidden(response)
          } else if (response.data.error !== 0) {
            this.handleApiError(response)
          }
        }
      },

      handleServerError(response) {
        this._showAlert(response.statusText)
      },

      handleUnauthorized () {
        this.$router.replace({name: 'login'})
      },

      handleForbidden (response) {
        this._showAlert(response.data.message)
      },

      handleApiError (response) {
        this._showAlert(response.data.message)
      },

      _showAlert (message) {
        this.$store.dispatch('createAlert', {type: 'warning', message: message})
      }
    }
  }
</script>
