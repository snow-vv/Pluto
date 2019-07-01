<template>
  <div class="gm-search-select" @click.stop="">
    <div class="input-box" @click="showList">
      <input
        type="text"
        class="search form-control"
        :disabled="disabled"
        :value="value"
        @keyup="onInput">
    </div>
    <div v-if="visible && filtered.length > 0" class="select">
      <ul>
        <li
          v-for="d in filtered"
          :key="d.id"
          :title="d.text"
          :class="{active: d.id==current, disabled: d.disabled}"
          @click="onSelect(d)"
          class="ellipsis">{{d.text}}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import debounce from '@/utils/debounce'

export default {
  props: {
    current: {
      type: [Number, String],
      default: ''
    },
    data: {
      type: Array,
      default: () => []
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },

  data () {
    return {
      key: '',
      visible: false
    }
  },

  computed: {
    value () {
      if (!this.current) return ''
      for (let i = 0; i < this.data.length; i++) {
        if (this.data[i].id === this.current) {
          return this.data[i].text
        }
      }
      return ''
    },

    filtered () {
      let key = this.key
      if (!key) return this.data
      return this.data.filter(x => x.text.indexOf(key) !== -1)
    }
  },

  methods: {
    showList () {
      if (!this.disabled) {
        this.visible = true
        document.addEventListener('click', this.closeOnDocumentClick, false)
      }
    },

    hideList () {
      document.removeEventListener('click', this.closeOnDocumentClick, false)
      this.visible = false
    },

    closeOnDocumentClick () {
      this.hideList()
    },

    onInput: debounce(function (e) {
      this.key = e.target.value.trim()
    }, 500),

    onSelect (data) {
      if (!data.disabled) {
        this.hideList()
        this.$emit('select', data)
      }
    }
  }
}
</script>

<style lang="less">
.gm-search-select {
  display: inline-block;
  position: relative;
  vertical-align: middle;
  width: 100%;

  ::-webkit-scrollbar {
    width: 3px;
  }

  ::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
  }

  ::-webkit-scrollbar-thumb {
    background: rgba(97, 171, 218, .5);
  }

  .input-box {
    position: relative;
    cursor: pointer;
    &:after {
      content: "";
      position: absolute;
      right: 0;
      top: 0;
      width: 34px;
      height: 34px;
      background: url(../../assets/img/icon-arrow.png) 50% 50% no-repeat;
    }
  }

  input {
    padding-right: 34px;
  }

  .select {
    position: absolute;
    left: 0;
    right: 0;
    top: 34px;
    z-index: 5;
    max-height: 200px;
    overflow: auto;
    border: 1px solid #3c8dbc;
    border-top: 0;
    background-color: #fff;
  }

  ul,
  li {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  li {
    padding: 6px;
    cursor: pointer;

    &:hover {
      color: #fff;
      background-color: #3c8dbc;
    }
    &.active {
      color: #444;
      background-color: #ddd;
    }
    &.disabled {
      background-color: #fff;
      cursor: not-allowed;
    }
  }
}
</style>
