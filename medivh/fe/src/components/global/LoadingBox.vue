<template>
  <div class="box box-primary">
    <transition name="fade">
      <loading-overlay v-show="showOverlay"></loading-overlay>
    </transition>
    <div class="box-header with-border">
      <h3 class="box-title">
        <slot name="title"></slot>
      </h3>
    </div>
    <div class="box-body">
      <slot name="body"></slot>
    </div>
    <div class="box-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
  import LoadingOverlay from '@/components/global/LoadingOverlay'

  export default {
    components: {LoadingOverlay},

    props: ['showOverlay']
  }
</script>
