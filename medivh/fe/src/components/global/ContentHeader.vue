<template>
  <section class="content-header">
    <h1>
      {{ contentHeader.title }}
      <small>
        {{ contentHeader.subTitle }}
      </small>
    </h1>
  </section>
</template>

<script>
  export default {
    data () {
      return {
        contentHeader: {}
      }
    },

    created () {
      this.buildContentHeader(this.$route)
    },

    watch: {
      $route (to, from) {
        this.buildContentHeader(to)
      }
    },

    methods: {
      buildContentHeader (route) {
        if (route.meta.contentHeader) {
          this.contentHeader = route.meta.contentHeader
        } else {
          this.contentHeader = {title: route.name}
        }
      }
    }
  }
</script>
