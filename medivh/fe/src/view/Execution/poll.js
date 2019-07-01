import http from '@/utils/networking'

const INTERVAL = 1 * 1000

export default function Poll(url, params) {
  this.url = url
  this.params = params
  this.timeId = null
}

Poll.prototype.start = function (callback) {
  this.callback = callback
  this.fetch()
  this.timeId = setInterval(() => {
    this.fetch()
  }, INTERVAL)
}

Poll.prototype.stop = function () {
  clearInterval(this.timeId)
}

Poll.prototype.fetch = function () {
  http.doGet(this.url, this.params).then(({data}) => {
    if (data.finish) {
      this.stop()
    }
    this.callback(data)
  })
}
