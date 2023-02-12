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
  //获取输入款内容
  mode(e) {
    mode = e.detail.value
  },
  degrees(e) {
    degrees = e.detail.value
  },
  //改变模式事件
  update() {
    let flag = false //表示是否可以成功预约
    if (mode == '' || degrees == '') {
      wx.showToast({
        icon: 'none',
        title: '请输入数字！',
      })
    } else if (mode < -1 || mode > 1) {
      wx.showToast({
        icon: 'none',
        title: '模式输入错误',
      })
    } else if (degrees < -1 || degrees == 0 || degrees > 1000) {
      wx.showToast({
        icon: 'none',
        title: '电量输入错误',
      })
    } else if (mode == -1 && degrees == -1) {
      wx.showToast({
        icon: 'none',
        title: '未作出修改',
      })
    } else {
      if (mode == 0) {
        type = 0
      } else {
        type = 1
      }
      degrees = parseInt(degrees)
      var mess = {
        "modeFlag": type,
        "degrees": degrees
      }
      wx.request({
        url: 'http://49.232.162.82:8180/api/change',
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
              app.globalData.pileInfo = result.data
            }
          }),
          console.log(res)
          if (res.data.code == 200) {
            /*wx.showToast({
              title: "修改成功",
            })
            */
            app.globalData.changeFlag = 0
            wx.navigateTo({
              url: '../../pages/users_pileInfos/index',
            });
          } else if (res.data.code == 201) {
            app.globalData.changeFlag = 1
            /*wx.showToast({
              icon: 'none',
              title: '修改失败，车已不在等待队列',
            })
            */
            wx.navigateTo({
              url: '../../pages/users_pileInfos/index',
            });
          }
        }
      })
    }
  },
  return_pre() {
    wx.navigateTo({
      url: '../../pages/users_option/index'
    })
  }
})