<template>
  <div class="skin-blue sidebar-mini wysihtml5-supported">
    <nav-bar></nav-bar>
    <side-bar></side-bar>
    <div class="content-wrapper" style="min-height: 916px;">
      <alert></alert>
      <content-header></content-header>
      <section class="content">
        <router-view></router-view>
      </section>
    </div>
  </div>
</template>

<script>
  import NavBar from '@/components/global/NavBar'
  import SideBar from '@/components/global/SideBar'
  import Alert from '@/components/global/Alert'
  import ContentHeader from '@/components/global/ContentHeader'

  export default {components: {SideBar, NavBar, Alert, ContentHeader}}
</script>
