export default {
  date (value, showTime) {
    if (!value) return value
    value = value * 1000
    var date = new Date(value)

    var year = date.getFullYear()
    var month = date.getMonth() + 1
    var day = date.getDate()

    var hour = date.getHours()
    var minutes = date.getMinutes()
    var seconds = date.getSeconds()

    var d = year + '-' + pad(month) + '-' + pad(day)
    var t = pad(hour) + ':' + pad(minutes) + ':' + pad(seconds)

    return d + (showTime ? ' ' + t : '')
  },

  json (value) {
    return value ? JSON.stringify(JSON.parse(value), null, 2) : ''
  }
}

function pad(n) {
  return n < 10 ? `0${n}` : n
}
