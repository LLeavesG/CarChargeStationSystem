//app.js

App({
  //onLaunch,onShow: options(path,query,scene,shareTicket,referrerInfo(appId,extraData))
  onLaunch: function (options) {

  },
  onShow: function (options) {},

  onHide: function () {

  },
  onError: function (msg) {

  },
  //options(path,query,isEntryPage)
  onPageNotFound: function (options) {

  },
  onLaunch: function () {

  },
  globalData: {
    token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1NjA3NTcyMSwianRpIjoiMTlkZjVlYTMtNWNjOC00NTBjLWFkODktMjM3ZTRlMTVhODkxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNjU2MDc1NzIxLCJleHAiOjE2NTYxNjIxMjF9.SQfUS5NCwyp5TAX9sDVGCEZ0MM-tyauEM5K9Kzg3xJA",
    userid: "", //登录参数
    usernames: "",
    pileInfo: {}, //充电桩信息
    orderInfo: {}, //订单信息
    bookFlag: -1,  //展示预约成功标志 0成功 1失败 -1不展示
    changeFlag: -1, //展示修改成功标志 0成功 1失败 -1不展示
  }
});