var api = require('./api')

const target = 'http://system.env:6001'

// 可以修改请求内容
const onProxyReq = proxyReq => {}

module.exports = api.reduce((result, curr) => {
    result[curr] = {
        target,
        onProxyReq,
        changeOrigin: true
    }
    return result
}, {})
