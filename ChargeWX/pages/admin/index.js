// pages/users_change_mode/index.js
const app = getApp()
let mode = ''
let type = ''
let degrees = 0

Page({

  /**
   * 页面的初始数据
   */
  data: {
    mode: '',
    degrees: 0,
    type: '',
    clientHeight: ''
  },
  onLoad() {
    var that = this
    wx.getSystemInfo({
      success: function (res) {
        console.log(res.windowHeight)
        that.setData({
          clientHeight: res.windowHeight
        });
      }
    })
  },
  goto_report()
  {
    wx.navigateTo({
      url: '../../pages/report/index',
    })
  }
    ,
     goto_hubinfo()
  {
    wx.navigateTo({
      url: '../../pages/hubinfo/index',
    })
  },
  goto_hubswitch()
  {
    wx.navigateTo({
      url: '../../pages/hubswitch/index',
    })
  },
  goto_waitinginfo()
  {
    wx.navigateTo({
      url: '../../pages/adWaitingInfo/index',
    })
  },
  goto_info()
  {
    wx.navigateTo({
      url: '../../pages/users_pileInfos/index',
    })
  }
  ,
  return_pre() {
    wx.navigateTo({
     
    })
  }
})