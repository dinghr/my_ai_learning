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
  }
}
