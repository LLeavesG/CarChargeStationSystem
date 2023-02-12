// pages/users/index.js
const app = getApp()
let mode = ''
let type = ''
let degrees = 0
let tokens = ''
Page({

    /**
     * 页面的初始数据
     */
    data: {
      mode: '',
      degrees: 0,
      type: '',
      clientHeight: '',
      tokens: '',
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
    //获取输入款内容
    mode(e) {
      mode = e.detail.value
    },
    degrees(e) {
      degrees = e.detail.value
    },
    //预约充电事件
    book_charge() {
      let flag = false //表示是否可以成功预约
      if (mode == '' || degrees == '') {
        wx.showToast({
          icon: 'none',
          title: '请输入数字！',
        })
      } else if (mode < 0 || mode > 1) {
        wx.showToast({
          icon: 'none',
          title: '模式输入错误',
        })
      } else if (degrees <= 0 || degrees > 1000) {
        wx.showToast({
          icon: 'none',
          title: '电量输入错误',
        })
      } else {
        if (mode == 0) {
          type = 'slow'
        } else {
          type = 'fast'
        }
        degrees = parseInt(degrees)
        var mess = {
          "mode": type,
          "degrees": degrees
        }
        wx.request({
          url: 'http://49.232.162.82:8180/api/charge',
          method: 'POST',
          data: JSON.stringify(mess),
          header: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + app.globalData.token
          },
          success: function (res) {
            wx.request({
                url: 'http://49.232.162.82:8180/api/getInfo',
                method: 'GET',
                header: {
                  "Content-Type": "application/x-www-form-urlencoded",
                  "Authorization": "Bearer " + app.globalData.token
                },
                success: function (result) {
                  console.log(result)
                  app.globalData.pileInfo = result.data.data
                }
              }),
              console.log(res)
            if (res.data.code == 200) {
              app.globalData.bookFlag = 0
              wx.navigateTo({
                url: '../../pages/users_pileInfos/index',
              });
            } else if (res.data.code == 201) {
              app.globalData.bookFlag = 1
              /*
              wx.showToast({
                             icon: 'none',
                             title: '模式输入错误',
                           })
              */
            } else if (res.data.code == 202) {
              app.globalData.bookFlag = 2
              /*wx.showToast({
                icon: 'none',
                title: '您有订单正在进行中，将为您跳转到该服务页面',
              });
              */
                wx.navigateTo({
                  url: '../../pages/users_pileInfos/index',
                })
            } else if (res.data.code == 203) {
              app.globalData.bookFlag = 3
              /*wx.showToast({
                icon: 'none',
                title: '当前充电桩已满，请稍后重试',
              });
              */
             wx.navigateTo({
              url: '../../pages/users_pileInfos/index',
            })
            }
          }
        })
      }
    }
  },






)