<template>
<div class="vc-dropdown" @click.stop="">
  <button
    type="button"
    @click="showList"
    class="btn btn-default add-task"
  ><slot></slot></button>
  <div v-if="options.length > 0 && visible" class="list">
    <ul>
      <li
        v-for="o in options"
        @click="onSelect(o)"
        class="ellipsis">{{o.text}}</li>
    </ul>
  </div>
</div>
</template>

<script>
export default {
  props: {
    options: {
      type: Array,
      default: () => []
    }
  },

  data () {
    return {
      visible: false
    }
  },

  methods: {
    showList () {
      this.visible = true
      document.addEventListener('click', this.closeOnDocumentClick, false)
    },

    hideList () {
      document.removeEventListener('click', this.closeOnDocumentClick, false)
      this.visible = false
    },

    closeOnDocumentClick () {
      this.hideList()
    },

    onSelect (o) {
      this.hideList()
      this.$emit('select', o)
    }
  }
}
</script>

<style lang="less">
.vc-dropdown {
  position: relative;
  display: inline-block;
  text-align: left;
  width: 100%;

  button {
    width: 100%;
  }

  .list {
    position: absolute;
    left: 0;
    top: 35px;
    z-index: 5;
    max-height: 300px;
    min-width: 100%;
    max-width: 500px;
    overflow-y: auto;
    border: 1px solid #ddd;
    background-color: #fff;
    &.show {
      display: block;
    }
  }

  ul,
  li {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  li {
    padding: 6px;
    cursor: default;
    &:hover {
      color: #fff;
      background-color: #3c8dbc;
    }
  }

  ::-webkit-scrollbar {
    width: 3px;
  }

  ::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
  }

  ::-webkit-scrollbar-thumb {
    background: rgba(97, 171, 218, .5);
  }
}
</style>
