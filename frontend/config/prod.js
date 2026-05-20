module.exports = {
  mini: {},
  h5: {
    publicPath: '.'
  },
  defineConstants: {
    // 生产环境 API 地址
    // 构建时可通过环境变量覆盖：TARO_APP_API_URL=https://api.example.com/api npm run build:weapp
    API_URL: JSON.stringify(process.env.TARO_APP_API_URL || 'https://your-domain.com/api')
  }
}
