<template>
  <div
    class="vc-model"
    :class="{show: show}"
    @click="click">
  <slot></slot>
</div>
</template>

<script>
export default {
  props: {
    show: {
      type: Boolean,
      default: false
    },
    onClick: {
      type: Function,
      default: () => {}
    }
  },

  beforeDestroy () {
    document.body.style.overflow = 'visible'
  },

  watch: {
    show (newValue) {
      if (document && document.body) {
        if (newValue) {
          document.body.style.overflow = 'hidden'
        } else {
          document.body.style.overflow = 'visible'
        }
      }
    }
  },

  methods: {
    click () {
      this.$emit('click')
    }
  }
}
</script>

<style lang="less">
.vc-model {
  display: none;
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 2000;
  background-color: #333;
  background-color: rgba(51, 51, 51, .7);

  &.show {
    display: block;
  }
}
</style>
