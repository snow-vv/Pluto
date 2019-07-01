<template>
<div class="vc-date-picker">
  <div
    class="input-box"
    @click="showSelect"
    :class="{disabled: disabled}">
    <input
      type="text"
      @input.stop=""
      @change="onChange"
      :disabled="disabled"
      :style="{width: width ? width+'px' : 'auto'}"
      :value="formatValue">
    <span
      :class="{clear: isClear}"
      @mouseenter="mouseEnter"
      @mouseleave="mouseLeave"
      @click="clear"></span>
  </div>

  <div
    v-show="visible"
    @click.stop=""
    class="date-picker">
    <div class="date-header">
      <div class="day-panel">
        <div class="prev">
          <span @click="yearClick(-1, true)">&lt;&lt;</span>
          <span @click="monthClick(-1)">&lt;</span>
        </div>
        <div class="value">
          <span @click="toggleState('year')" class="year">{{nowYear}} 年</span>
          <span @click="toggleState('month')" class="month">{{nowMonth + 1}} 月</span>
        </div>
        <div class="next">
          <span @click="monthClick(1)">&gt;</span>
          <span @click="yearClick(1, true)">&gt;&gt;</span>
        </div>
      </div>

      <div v-show="state == 'year'" class="year-panel">
        <div @click="yearRangeClick(-1)" class="prev"><span>&lt;&lt;</span></div>
        <div class="value">
          <span>{{yearStart}} 年 - {{yearStart+9}} 年</span>
        </div>
        <div @click="yearRangeClick(1)" class="next"><span>&gt;&gt;</span></div>
      </div>
      <div v-show="state == 'month'" class="month-panel">
        <div @click="yearClick(-1)" class="prev"><span>&lt;&lt;</span></div>
        <div class="value">
          <span @click="toggleState('year')">{{nowYear}} 年</span>
        </div>
        <div @click="yearClick(1)" class="next"><span>&gt;&gt;</span></div>
      </div>
      <div
        v-if="time"
        v-show="state == 'time'"
        class="time-panel"
      >{{toString()}}</div>
    </div>

    <div v-if="date.length" class="date-body">
      <table class="day-panel">
        <thead>
          <tr class="date-days">
            <th v-for="day in days"><span>{{day}}</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in 6">
            <td v-for="j in 7"
              :class="[date[getIdx(i,j)].status, {disabled:date[getIdx(i,j)].disabled}]"
              :date="date[getIdx(i,j)].date"
              @click="pickDate(getIdx(i,j))">
              <span>{{date[getIdx(i,j)].text}}</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-show="state == 'year'" class="year-panel">
        <table>
          <tr v-for="i in 4">
            <td
              v-for="j in 3"
              :class="{first: i == 1 && j == 1, last: i == 4 && j == 3, active: nowYear == getYearByIndex(i-1, j-1, yearStart)}">
              <span @click="selectYear(getYearByIndex(i-1, j-1, yearStart), i-1, j-1)">{{getYearByIndex(i-1, j-1, yearStart)}}</span>
            </td>
          </tr>
        </table>
      </div>

      <div v-show="state == 'month'" class="month-panel">
        <table>
          <tr v-for="i in 4">
            <td
              v-for="j in 3"
              :class="{active: nowMonth == (i-1) * 3 + j-1}">
              <span @click="selectMonth(i-1, j-1)">{{months[(i-1) * 3 + j-1]}}月</span>
            </td>
          </tr>
        </table>
      </div>

      <div
        v-if="time"
        v-show="state == 'time'"
        class="time-panel">
        <div class="list">
          <ul><li v-for="i in 24" @click="selectHour(i-1)" :class="{active: i-1 == nowHour}">{{i-1|padding}}</li></ul>
        </div>
        <div class="list">
          <ul><li v-for="i in 60" @click="selectMinute(i-1)" :class="{active: i-1 == nowMinute}">{{i-1|padding}}</li></ul>
        </div>
        <div class="list">
          <ul><li v-for="i in 60" @click="selectSecond(i-1)" :class="{active: i-1 == nowSecond}">{{i-1|padding}}</li></ul>
        </div>
      </div>
    </div>

    <div
      v-if="time"
      v-show="state == 'time' || state == 'date'" class="date-footer">
      <span @click="toggleState('time')">{{state == 'date' ? '选择时间' : '返回'}}</span>
    </div>
  </div>
</div>
</template>

<script>
// ref https://github.com/Bubblings/vue-date-picker
const DATE_RE = /^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:(?:\s*|T)(\d{1,2}):(\d{1,2}):(\d{1,2}))?$/

export default {
  props: {
    value: {
      type: [String, Number],
      default: ''
    },
    format: {
      type: String,
      // YYYY-MM-DD HH:mm:ss
      default: 'YYYY-MM-DD'
    },
    time: {
      type: Boolean,
      default: false
    },
    // false value
    min: {
      type: [Date, Object, String],
      default: null
    },
    max: {
      type: [Date, Object, String],
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    },
    clearable: {
      type: Boolean,
      default: false
    },
    width: {
      type: Number,
      default: 0
    }
  },

  data () {
    return {
      visible: false,
      isClear: false,
      now: new Date(),
      // year, month, date, time
      state: 'date',
      date: [],
      yearStart: 0,
      month: [],
      months: ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'],
      days: ['日', '一', '二', '三', '四', '五', '六']
    }
  },

  computed: {
    nowYear () {
      return this.now.getFullYear()
    },
    nowMonth () {
      return this.now.getMonth()
    },
    nowDate () {
      return this.now.getDate()
    },
    nowHour () {
      return this.now.getHours()
    },
    nowMinute () {
      return this.now.getMinutes()
    },
    nowSecond () {
      return this.now.getSeconds()
    },
    formatValue () {
      let t = this.parse(this.value)
      return t ? this.toString(t) : ''
    }
  },

  methods: {
    hide () {
      document.removeEventListener('click', this.closeOnDocumentClick, false)
      this.visible = false
    },

    show () {
      this.updateDate()
      this.visible = true
      document.addEventListener('click', this.closeOnDocumentClick, false)
    },

    closeOnDocumentClick (e) {
      if (!this.$el.contains(e.target)) {
        this.hide()
      }
    },

    getIdx(i, j) {
      return (i - 1) * 7 + j - 1
    },

    mouseEnter () {
      if (this.clearable && this.value) {
        this.isClear = true
      }
    },
    mouseLeave () {
      this.isClear = false
    },
    clear (e) {
      if (this.isClear) {
        e.stopPropagation()
        this.now = new Date()
        this.$emit('input', '', 0)
        this.$emit('clear')
      }
    },

    onChange (e) {
      let value = e.target.value.trim()
      if (!value) {
        this.hide()
        this.now = new Date()
        this.$emit('input', '', 0)
        return
      }

      let v = this.parse(value)
      if (v && !this.isDisabled(v)) {
        this.now = v
        this.change()
      }
      e.target.value = this.formatValue
    },

    showSelect (e) {
      if (this.disabled || this.visible) return
      if (!this.visible && this.value) {
        this.now = this.parse(this.value) || new Date()
      }
      this.show()
    },

    toggleState (state) {
      if (state !== this.state) {
        this.state = state
        if (state === 'year') {
          let year = this.nowYear
          this.yearStart = year - year % 10
        }
      } else if (state !== 'date') {
        this.state = 'date'
      }
    },

    getYearByIndex(i, j, start) {
      return start + i * 3 + j - 1
    },

    yearRangeClick (dir) {
      let start = this.yearStart
      this.yearStart = start - start % 10 + 10 * dir
    },

    selectYear (year, i, j) {
      if (i === 0 && j === 0) {
        this.yearRangeClick(-1)
      } else if (i === 3 && j === 2) {
        this.yearRangeClick(1)
      } else {
        this.now.setFullYear(year)
        this.now = new Date(this.now)
        this.state = 'month'
      }
    },

    selectMonth (i, j) {
      this.now.setMonth(i * 3 + j)
      this.now = new Date(this.now)
      this.updateDate()
      this.state = 'date'
    },

    yearClick (flag, update) {
      this.now.setFullYear(this.nowYear + flag)
      this.now = new Date(this.now)
      if (update) {
        this.updateDate()
      }
    },

    monthClick (flag) {
      this.now.setMonth(this.nowMonth + flag)
      this.now = new Date(this.now)
      this.updateDate()
    },

    selectHour (i) {
      this.now.setHours(i)
      this.now = new Date(this.now)
      this.change()
    },

    selectMinute (i) {
      this.now.setMinutes(i)
      this.now = new Date(this.now)
      this.change()
    },

    selectSecond (i) {
      this.now.setSeconds(i)
      this.now = new Date(this.now)
      this.change()
    },

    pickDate (index) {
      let data = this.date[index]
      if (data.disabled) return
      this.hide()
      let date = new Date(data.time)
      date.setHours(this.nowHour, this.nowMinute, this.nowSecond)
      this.now = date
      this.change()
    },

    change () {
      if (this.min && this.now < this.min) {
        this.now = new Date(this.min)
      }
      if (this.max && this.now > this.max) {
        this.now = new Date(this.max)
      }
      this.$emit('input', this.toString(), this.now.getTime())
    },

    isDisabled (t) {
      if (this.min) {
        let min = new Date(this.min)
        min.setHours(0, 0, 0, 0)
        if (t < min) return true
      }
      if (this.max) {
        let max = new Date(this.max)
        max.setHours(23, 59, 59, 999)
        if (t > max) return true
      }
      return false
    },

    updateDate () {
      let isDisabled = this.isDisabled
      let arr = []
      let time = new Date(this.now)
      // the first day
      time.setMonth(time.getMonth(), 1)
      let curFirstDay = time.getDay()
      if (curFirstDay === 0) {
        curFirstDay = 7
      }
      // the last day
      time.setDate(0)
      let lastDayCount = time.getDate()

      for (let i = curFirstDay; i > 0; i--) {
        let t = new Date(time.getFullYear(), time.getMonth(), lastDayCount - i + 1)
        arr.push({
          text: lastDayCount - i + 1,
          time: t,
          status: 'date-pass',
          disabled: isDisabled(t)
        })
      }

      // the last day of this month
      time.setMonth(time.getMonth() + 2, 0)
      let curDayCount = time.getDate()
      // fix bug when month change
      time.setDate(1)

      let value = this.parse(this.value)
      if (value) {
        value = this.toString(value, 'YYYY-MM-DD')
      }

      for (let i = 0; i < curDayCount; i++) {
        let t = new Date(time.getFullYear(), time.getMonth(), i + 1)
        arr.push({
          text: i + 1,
          time: t,
          status: this.toString(t, 'YYYY-MM-DD') === value ? 'active' : '',
          disabled: isDisabled(t)
        })
      }

      let j = 1
      while (arr.length < 42) {
        let t = new Date(time.getFullYear(), time.getMonth() + 1, j)
        arr.push({
          text: j,
          time: t,
          status: 'date-future',
          disabled: isDisabled(t)
        })
        j++
      }

      this.date = arr
    },

    // 仅支持
    // unix ms, YYYY-MM-DD, YYYY-MM-DD HH:mm:ss, YYYY-MM-DDTHH:mm:ss
    parse (str) {
      let time
      if (typeof str === 'number') {
        time = new Date(str)
      } else {
        let m = str.match(DATE_RE)
        if (!m) return null
        time = m[4]
        ? new Date(m[1], m[2] - 1, m[3], m[4], m[5], m[6])
        : new Date(m[1], m[2] - 1, m[3])
      }
      return isNaN(time.getTime()) ? null : time
    },

    toString (time = this.now, format = this.format) {
      let year = time.getFullYear()
      let month = time.getMonth() + 1
      let date = time.getDate()
      let monthName = time.getMonth() + 1
      let hour = time.getHours()
      let minute = time.getMinutes()
      let second = time.getSeconds()
      let pad = v => v >= 10 ? v : '0' + v

      const map = {
        YYYY: year,
        MM: pad(month),
        M: month,
        DD: pad(date),
        D: date,
        HH: pad(hour),
        H: hour,
        mm: pad(minute),
        m: minute,
        ss: pad(second),
        s: second
      }

      return format.replace(/Y+|M+|D+|H+|m+|s+/g, str => map[str])
    }
  },

  filters: {
    padding (v) {
      return v >= 10 ? v : '0' + v
    }
  }
}
</script>

<style lang="less">
.vc-date-picker {
  position: relative;
  display: inline-block;
  font-size: 14px;

  ul,
  li {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .input-box input {
    height: 30px;
    line-height: 30px;
    padding: 0 32px 0 10px;
    border: 1px solid #B9B9B9;
    font-size: 14px;
    color: #333;
  }
  .input-box span {
    position: absolute;
    right: 4px;
    top: 4px;
    width: 22px;
    height: 22px;
    background: url(../../assets/img/icon-select.png) no-repeat;
    &.clear {
      background: url(../../assets/img/close.png) 50% 50% no-repeat;
      background-size: 50% 50%;
    }
  }
  .input-box.disabled span {
    cursor: default;
  }

  .date-picker {
    position: absolute;
    left: 0;
    top: 100%;
    z-index: 1000;
    width: 240px;
    margin-top: 5px;
    background-color: #fff;
    box-shadow: 0 1px 6px rgba(0,0,0,.2);
    color: rgba(0,0,0,.65);
    user-select: none;
  }

  .date-header {
    position: relative;
    text-align: center;
    height: 40px;
    line-height: 40px;

    span {
      display: inline-block;
      cursor: pointer;
    }

    .prev,
    .next {
      position: absolute;
      top: 0;
      color: rgba(0,0,0,.43);
      span {
        padding: 0 5px;
      }
    }
    .prev {
      left: 8px;
    }
    .next {
      right: 8px;
    }

    .value {
      font-weight: 700;
    }
    .year {
      margin-right: 10px;
    }
  }

  .date-body {
    position: relative;
    border-top: 1px solid #e9e9e9;
    padding: 4px 8px;
  }

  .date-footer {
    border-top: 1px solid #e9e9e9;
    text-align: center;
    span {
      display: inline-block;
      padding: 8px 10px;
      cursor: pointer;
    }
  }

  .year-panel,
  .month-panel,
  .time-panel {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    background-color: #fff;
  }

  // day panel
  table {
    width: 100%;
    border-collapse: collapse;
    border-spacing: 0;
  }

  th,
  td {
    text-align: center;
    padding: 3px 0;
  }

  th span,
  td span {
    display: inline-block;
    width: 24px;
    height: 24px;
    line-height: 24px;
  }
  td span {
    cursor: pointer;
  }

  td.date-pass span,
  td.date-future span,
  td.disabled span {
    color: rgba(0,0,0,.25);
  }

  td:hover span {
    background-color: #ecf6fd;
  }
  td.disabled {
    cursor: not-allowed;
  }
  td.disabled:hover span {
    background-color: #fff;
    cursor: not-allowed;
  }
  td.active span {
    color: #fff;
    background-color: #108ee9;
  }

  .date-body .month-panel td,
  .date-body .year-panel td {
    height: 54.5px;
    vertical-align: middle;

    &:hover {
      color: #108ee9;
    }

    span {
      width: auto;
      height: auto;
      padding: 0 10px;
      height: 30px;
      line-height: 30px;
      cursor: pointer;
    }
  }

  .date-body .year-panel td {
    &.first,
    &.last {
      color: rgba(0,0,0,.25);
    }
  }

  .date-body .time-panel .list {
    float: left;
    width: 33.333333%;
    height: 100%;
    text-align: center;
    overflow: auto;
  }

  .date-body .time-panel li {
    height: 30px;
    line-height: 30px;
    cursor: pointer;

    &:hover {
      background: #ecf6fd;
    }
    &.active {
      background: #f7f7f7;
      font-weight: 700;
    }
  }
}
</style>
