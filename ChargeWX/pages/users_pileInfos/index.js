// pages/users_pileInfo/index.js
const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    mes: "123",
    fast_charge: "",
    fast_wait: "",
    slow_charge: "",
    slow_wait: "",
    first: "0",
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    var that = this
    if (app.globalData.bookFlag != -1) {
      if (app.globalData.bookFlag == 0) //预约成功
      {
        wx.showToast({
          icon: 'none',
          title: '预约成功',
        })

      }
      if (app.globalData.bookFlag == 1) //预约失败 模式输入错误
      {
        wx.showToast({
          icon: 'none',
          title: '预约失败 模式输入错误',
        })
      }
      if (app.globalData.bookFlag == 2) //预约失败 有订单正在进行中
      {
        wx.showToast({
          icon: 'none',
          title: '预约失败 有订单正在进行中',
        })
      }
      if (app.globalData.bookFlag == 3) //预约失败 当前充电桩已满
      {
        wx.showToast({
          icon: 'none',
          title: '预约失败 当前充电桩已满',
        })
      }
      app.globalData.bookFlag = -1
    }
    if (app.globalData.changeFlag != -1) {
      if (app.globalData.changeFlag == 0) {
        wx.showToast({
          title: "修改成功",
        })
      } else if (app.globalData.changeFlag == 1) {
        wx.showToast({
          icon: 'none',
          title: '修改失败，车已不在等待队列',
        })
      }
      app.globalData.changeFlag = -1
    }
    wx.request({
      url: 'http://49.232.162.82:8180/api/getInfo',
      method: 'GET',

      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + app.globalData.token

      },
      success: function (res) {
        //将获取到的json数据，存在名字叫list的这个数组中
        console.log(res);
        var json2 = JSON.parse(res.data.data);
        console.log(json2);
        var fast_charge0 = json2["fast_charge"]["0"]["0"]
        var fast_arr0 = json2["fast_charge"]["0"]["1"]
        var fast_arr00 = json2["fast_charge"]["0"]["2"]

        var fast_charge1 = json2["fast_charge"]["1"]["0"]
        var fast_arr1 = json2["fast_charge"]["1"]["1"]
        var fast_arr11 = json2["fast_charge"]["1"]["2"]

        var slow_charge0 = json2["slow_charge"]["0"]["0"]
        var slow_arr0 = json2["slow_charge"]["0"]["1"]
        var slow_arr00 = json2["slow_charge"]["0"]["2"]


        var slow_charge1 = json2["slow_charge"]["1"]["0"]
        var slow_arr1 = json2["slow_charge"]["1"]["1"]
        var slow_arr11 = json2["slow_charge"]["1"]["2"]

        var slow_charge2 = json2["slow_charge"]["2"]["0"]
        var slow_arr2 = json2["slow_charge"]["2"]["1"]
        var slow_arr22 = json2["slow_charge"]["2"]["2"]


        var list_fast = [];
        var list_slow = [];

        for (var i = 0; i < 10; i++) {
          if (json2["fast_wait"][i] != undefined) {
            console.log(json2["fast_wait"][i])
            list_fast.push(json2["fast_wait"][i])
          }
        }
        console.log(that.data.list_fast)
        for (var i = 0; i < 10; i++) {
          if (json2["slow_wait"][i] != undefined) {
            list_slow.push(json2["slow_wait"][i])
            console.log(json2["slow_wait"][i])

          }
        }
        console.log(that.data.list_fast)
        console.log(json2["fast_wait"]["0"])
        that.setData({
          fast_charge0: fast_charge0,
          fast_charge1: fast_charge1,
          slow_charge0: slow_charge0,
          slow_charge1: slow_charge1,
          slow_charge2: slow_charge2,
          fast_arr0: fast_arr0,
          fast_arr1: fast_arr1,
          slow_arr0: slow_arr0,
          slow_arr1: slow_arr1,
          slow_arr2: slow_arr2,
          fast_arr00: fast_arr00,
          fast_arr11: fast_arr11,
          slow_arr00: slow_arr00,
          slow_arr11: slow_arr11,
          slow_arr22: slow_arr22,
          list_slow: list_slow,
          list_fast: list_fast
          //res代表success函数的事件对，data是固定的，list是数组
        })
        console.log(that.data.list_fast)

      }
    })
  },

  cancel() {
    wx.navigateTo({
      url: '../../pages/users_option/index'
    })
  },
  

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {
    console.log(this.data.mes["0"])
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },
  getinfo() {

  }
})