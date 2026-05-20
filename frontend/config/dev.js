module.exports = {
  logger: {
    quiet: false,
    stats: true
  },
  mini: {},
  h5: {
    publicPath: '/',
    devServer: {
      port: 10086,
      historyApiFallback: {
        index: '/index.html',
        rewrites: [
          { from: /^\/[^.]*$/, to: '/index.html' }
        ]
      },
      static: {
        publicPath: '/',
      },
    }
  },
  defineConstants: {
    // 开发环境 API 地址（本地后端）
    API_URL: '"http://localhost:8000/api"'
  }
}
