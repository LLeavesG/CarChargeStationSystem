// pages/users_option/index.js
const app = getApp()
let queueNum = ''
let waitNum = ''
let pileInfo = ''
let orderInfo = ''
Page({

  /**
   * 页面的初始数据
   */
  data: {
    queueNum: '',
    waitNum: '',
    pileInfo: '',
    orderInfo: '',
  },

  /**
   * 生命周期函数--监听页面加载
   */
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
  //查看充电桩状态
  show_pile_info() {
    wx.request({
      url: 'http://49.232.162.82:8180/api/getInfo',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + app.globalData.token

      },
      success: function (res) {
        console.log(res)
        if (res.data.code == 200) {
          app.globalData.pileInfo = res.data


          wx.navigateTo({
            url: '../../pages/users_pileInfos/index',
          });
        }
      }
    })
  },

  //修改充电模式
  change_mode() {
    wx.navigateTo({
      url: '../../pages/users_change_mode/index'
    })
  },
  //查看订单信息
  show_order_info() {
    wx.request({
      url: 'http://49.232.162.82:8180/api/getOrderInfo',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + app.globalData.token

      },
      success: function (res) {
        console.log(res)
        if (res.data.code == 200) {
          app.globalData.orderInfo = res.data.data

          wx.navigateTo({
            url: '../../pages/users_showInfo/index',
          });

        } else if (res.data.code == 201) {
          wx.showToast({
            icon: 'none',
            title: "没有在进行的订单",
          });
          setTimeout(function () {
            wx.navigateTo({
              url: '../../pages/users_option/index',
            });
          }, 2000)
        }
      }
    })
  },
  //查询排队号
  show_queue_num() {
    wx.request({
      url: 'http://49.232.162.82:8180/api/getLineNum',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + app.globalData.token

      },
      success: function (res) {
        console.log(res)
        if (res.data.code == 200) {
          queueNum = res.data.data
          wx.showToast({
            icon: 'none',
            title: queueNum,
          })
        } else if (res.data.code == 201) {
          wx.showToast({
            icon: 'none',
            title: "你的车不在排队，可能已经在充电或充电完毕",
          })
        }
      }
    })
  },
  //查询等待数量
  show_waiting_num() {
    wx.request({
      url: 'http://49.232.162.82:8180/api/getBeforeNum',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + app.globalData.token
      },
      success: function (res) {
        console.log(res)
        if (res.data.code == 200) {
          waitNum = res.data.data
          wx.showToast({
            icon: 'none',
            title: waitNum,
          })
        } else if (res.data.code == 201) {
          wx.showToast({
            icon: 'none',
            title: "该模式前面没有车在等待了",
          })
        }
      }
    })

  },
  //取消充电
  cancel() {
    wx.request({
      url: 'http://49.232.162.82:8180/api/cancel',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + app.globalData.token

      },
      success: function (res) {
        console.log(res)
        if (res.data.code == 200) {
          wx.showToast({
            icon: 'none',
            title: '成功取消订单',
          })
        } else if (res.data.code == 201) {
          wx.showToast({
            icon: 'none',
            title: '取消失败，当前没有订单'
          })
        }
      }
    })
  },
  //返回上一级
  submit() {
    wx.navigateTo({
      url: '../../pages/users/index'
    })
  },
  goto_users() {
    wx.navigateTo({
      url: '../../pages/users/index'
    })
  }
})