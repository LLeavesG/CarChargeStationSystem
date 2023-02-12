//index.js
//获取应用实例
const app = getApp()
 let username=''
 let password=''
Page({
  data: {
    username: '',
    password: '',
    clientHeight:''
  },
  onLoad(){
    var that=this
    wx.getSystemInfo({ 
      success: function (res) { 
        console.log(res.windowHeight)
          that.setData({ 
              clientHeight:res.windowHeight
        }); 
      } 
    }) 
    username= '';
    password= '';
  },
  
  //获取输入款内容
  content(e){
    username=e.detail.value
  },
  password(e){
    password=e.detail.value
  },
  //登录事件
  go_registe(){
    let flag = false  //表示账户是否存在,false为初始值
    
    if(username=='')
    {
      wx.showToast({
        icon:'none',
        title: '账号不能为空',
        duration: 1000
      })
    }else if(password==''){
      wx.showToast({
        icon:'none',
        title: '密码不能为空',
        duration: 1000
      })
    }else if(username.length < 5 || username.length > 20 ){
        wx.showToast({
            icon:'none',
            title: '用户名长度不符合规范，应大于5且小于20字符',
            duration: 1000

          })
    }else if(password.length < 10 || password.length > 20 ){ 
        wx.showToast({
            icon:'none',
            title: '密码长度不符合规范，应大于10且小于20字符',
            duration: 1000

          })
    }
    else{
      var mess = {
        "username" : username,
        "password" : password
      }
      console.log(mess);

      wx.request({
        url: 'http://49.232.162.82:8180/api/registe',
        method: 'POST',
        data: JSON.stringify(mess),
        header: {
        "Content-Type": "application/x-www-form-urlencoded"
        
        },
        success: function (res) {
          console.log(res)
          if(res.data.code == 200){
            app.globalData.userid = res.userid;
            wx.showToast({
                title : "注册成功",
                icon:'none',
                duration: 2000,
              });
                        
            setTimeout(function () {
              wx.navigateBack({
                delta: 2        
            })
            }, 2000) //延迟时间 这里是1秒
                      
          }
          else if(res.data.code == 202){
            wx.showToast({
              title : "用户名已存在",
              icon:'none',
                duration: 1000
            });
          }
          else if(res.data.code == 201){
            wx.showToast({
              title : "用户名或密码不符合规范，应仅包含数字和字母/n用户名长度应为5-20字符，密码长度应为10-20字符",
              icon:'none',
                duration: 1000
            });
          }
          else{
            wx.showToast({
              title : "错误，请联系管理员",
              icon:'none',
                duration: 1000
            });
          }
        }
      })
      
    }
  },
})
 
