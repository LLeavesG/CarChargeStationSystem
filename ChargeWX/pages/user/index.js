const app = getApp()

Page({
    data: {
      src:"../../picture/OIP-C.png",
      hasUserInfo: false,
      canIUseGetUserProfile: false,
      username :"",
    },
    onShow() {
      if(app.globalData.token!=""){
        this.setData({
          hasUserInfo: true,
          username : app.globalData.usernames
        });
        var that = this;
        console.log(this.data.username)
      }    
    },
    getUserProfile(e) {
      // 推荐使用wx.getUserProfile获取用户信息，开发者每次通过该接口获取用户个人信息均需用户确认
      // 开发者妥善保管用户快速填写的头像昵称，避免重复弹窗
        
      
    },
    getUserInfo(e) {
      // 不推荐使用getUserInfo获取用户信息，预计自2021年4月13日起，getUserInfo将不再弹出弹窗，并直接返回匿名的用户个人信息
      this.setData({
        userInfo: e.detail.userInfo,
        hasUserInfo: true
      })
      
        
    },
  })