export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/ai-chat/index',
    'pages/profile/index',
    'pages/wish-pool/index',
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#B78134',
    navigationBarTitleText: 'AI助学',
    navigationBarTextStyle: 'white'
  },
  tabBar: {
    color: '#8B7355',
    selectedColor: '#B78134',
    backgroundColor: '#FFF8E7',
    borderStyle: 'white',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: 'assets/tabbar/home.png',
        selectedIconPath: 'assets/tabbar/home-active.png'
      },
      {
        pagePath: 'pages/ai-chat/index',
        text: 'AI学',
        iconPath: 'assets/tabbar/ai.png',
        selectedIconPath: 'assets/tabbar/ai-active.png'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
        iconPath: 'assets/tabbar/profile.png',
        selectedIconPath: 'assets/tabbar/profile-active.png'
      }
    ]
  }
})
