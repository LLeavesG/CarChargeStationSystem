// pages/report/index.js


const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    var that = this
    wx.request({
      url: 'http://49.232.162.82:8180/api/getReportForm',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization" : "Bearer " + app.globalData.token

      },
      
      success: function (res) {
        //将获取到的json数据，存在名字叫list的这个数组中
        console.log(res)
        var json2 = JSON.parse(res.data.data);
        var key;
        for (key in json2)
        {
            console.log(key);
            json2[key]["chargeHub_id"] = key;
        }
        console.log(json2);
        that.setData({
          dataList: json2
          //res代表success函数的事件对，data是固定的，list是数组
        })
      }
    })

    wx.getSystemInfo({
      success: function (res) {
        console.log(res.windowHeight)
        that.setData({
          clientHeight: res.windowHeight
        });
      }
    })

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

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

  }
})