const process = require('child_process');
const request = require("request");
const {BrowserWindow} = require('electron');
const ws = require("nodejs-websocket");
pythonapi = require('./pythonapi');

var control = {
	mainWindow: '',		// webview 窗件
	is_start: false,	// 首次连接服务器是否成功
	is_net_ok: false,	// 网络是否连通
	net_timer: 0,		// 网络探测定时器


	//导航
	navigat: function( nav_json ){
		//创建窗口
		var create_win = function(){
			var childWin = new BrowserWindow({parent: control.mainWindow, modal: true, show: false,frame: false,transparent: true})
			childWin.once('ready-to-show',() => {childWin.show()})
			return childWin
		}

		var close_win = function(){
			if( !control.childWin.isDestroyed() ){
				control.childWin.close();
			}
			control.childWin = "";
		}

		//console.log( typeof(nav_json) );
		try {
			//var nav_json = JSON.parse( json );
			if(typeof(nav_json)=='object'){
				// event ：'open' 弹出窗口
				var rx=/^https?:\/\//i;
				var url = nav_json.url;
				if(!rx.test(url)) url = "file:///"+__dirname+"/html/"+ url;
				url = url.replace(/\\/g, '/');

				if ( nav_json.event == 'open'){
					if( typeof(this.childWin) != 'object' ){
						this.childWin = create_win();
					}else if( this.childWin.isDestroyed() ){
						this.childWin = create_win();
					}

					if (nav_json.size){
						var w = nav_json.size.width;
						var h = nav_json.size.height
						this.childWin.setSize(w,h);
						this.childWin.center();
					}
					var currentURL = this.childWin.webContents.getURL();
					if (currentURL != url) this.childWin.loadURL(url)

					if (nav_json.timer){
						if( typeof(nav_json.timer)=='number' ){
							setTimeout(function(){close_win();}, nav_json.timer * 1000)
						}
					}
				}
				// event : 'self' 当前窗口
				if ( nav_json.event == 'self'){
					control.mainWindow.loadURL(url);
				}
				// event : 'close' 关闭弹出窗口
				if (nav_json.event == 'close'){
					if (typeof(this.childWin) == 'object'){
						close_win()
					}else{
						control.mainWindow.loadURL("file:///"+__dirname+"/html/index.html");
					}
				}
			}
		}catch(err){
			console.log("err:"+err);
		}
	},


	//内部通信服务端
	start_websocket: function(){
		console.log("开始建立连接...")

		var server = ws.createServer(function(conn){
		    conn.on("text", function (str) {
			    //console.log(str);
			    var json_str = JSON.parse(str);		//字符串转json

		        if (json_str.t == 'nav'){			//如果是导航消息，直接在这里处理
			        control.navigat(json_str);
		    	}else{
			        control.mainWindow.webContents.send('public',json_str);
				}
		    })
		    conn.on("close", function (code, reason) {
		        console.log("关闭连接")
		    });
		    conn.on("error", function (code, reason) {
		        console.log("异常关闭")
		    });
		}).listen(8103)

		console.log("WebSocket建立完毕")
	},

	Init: function(mainWindow){
		this.mainWindow = mainWindow;
		console.log('这里开始');
		this.start_websocket();
	}
}

module.exports = control;