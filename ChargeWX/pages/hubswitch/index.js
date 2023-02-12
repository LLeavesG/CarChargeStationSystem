const app = getApp()
var pageObj = {
  data: {
    isChecked1: -1,
    isChecked2: -1,
    isChecked3: -1,
    isChecked4: -1,
    isChecked5: -1

  },
  onLoad(options) {
    var that = this
    wx.request({
      url: 'http://49.232.162.82:8180/api/getHubState',
      method: 'GET',
      header: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization" : "Bearer " + app.globalData.token
      },
      success: function (res) {
   
        console.log(res);
        var json2 = JSON.parse(res.data.data);
        var key;        
        var on = "on";
        var off = "off";
        console.log(json2.f0)
        for (key in json2)
        {
            console.log("state  "+json2[key]["state"]);
            if(json2[key]["state"] == on )
            {json2[key]["state"] = 1;console.log("修改on"+key+"为"+json2[key]["state"]);}
            else if(json2[key]["state"] == off)
            {json2[key]["state"] = 0;console.log("修改off"+key+"为"+json2[key]["state"]);}
            
        }
        that.isChecked1 = json2.s0.state
        console.log(that.isChecked1)
        that.setData({
          "isChecked1" : json2.s0.state,
          "isChecked2" : json2.s1.state,
          "isChecked3" : json2.s2.state,
          "isChecked4" : json2.f0.state,
          "isChecked5" : json2.f1.state
        })
      }
    })
  }
 
};
var urlc ='http://49.232.162.82:8180//api/closeHub/';
var urlo ='http://49.232.162.82:8180//api/openHub/';
var urlts =''
for (var i = 1; i < 6; ++i) {
  (function (i) {
    pageObj['changeSwitch' + i] = function (e) {
      console.log(`switch${i}发生change事件，携带值为`, e.detail.value)
      if (e.detail.value == false) {
        urlts = urlc
      }
      else
      {
        urlts = urlo
      }
      if (i<4) {
         var a= i -1
        urlts=urlts+'slow/'+a
      }
      if (i>3) {
        var a= i -4
        urlts=urlts+'fast/'+a
     } console.log(urlts)
      wx.request({
        url: urlts,
        method: 'GET',
        header: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization" : "Bearer " + app.globalData.token
        },
        success: function (res) { 
          if(res.data.code == 200){
            wx.showToast({
              title : "操作成功",
            });}
          else
            {
              wx.showToast({
                title : "操作失败",
              });
            }
          console.log(res);
          console.log("changedData")}
      });
      urlts =''
      var changedData = {};
      changedData['isChecked' + i] = (this.data['isChecked' + i]+1) %2;
      console.log(changedData['isChecked' + i]);
      this.setData(changedData);
    }
  })(i)
}
Page(
 
   
    pageObj
  );

  

