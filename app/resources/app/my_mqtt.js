const process = require('child_process');
const {BrowserWindow} = require('electron');
const mqtt = require('mqtt');

var my_mqtt = {
	mainWindow:'',		// webview 窗件
	childWin:'',		// 子窗件
	conf: '',
	init: function(mainWindow,checkfunc){
		this.mainWindow = mainWindow;

		// 使用Python 数据接口获取配置数据
		var childSync = pythonapi.run('getconfig');
		if (childSync =='' ) return false;

		this.conf = JSON.parse(childSync.toString());

		var client = mqtt.connect(config.mqtt.server, {
			username: (my_mqtt.conf.mqtt_name).toString(),
			password: (my_mqtt.conf.mqtt_pass).toString(),
			clientId: (my_mqtt.conf.clientid).toString()
		});

		//建立连接成功，订阅主题
		client.on('connect', function() {
			var topic = '/'+my_mqtt.conf.clientid+'/sys/nav';		// 主题：导航
			client.subscribe(topic, {qos: 1});
			var topic = '/'+my_mqtt.conf.clientid+'/sys/info';		// 主题：系统消息
			client.subscribe(topic, {qos: 1});
			var topic = '/'+my_mqtt.conf.clientid+'/sys/admin';		// 主题：管理
			client.subscribe(topic, {qos: 1});

			if (typeof(checkfunc)=='function') checkfunc( my_mqtt.conf )

			//一系列简单接口处理
			//client.publish( '/top/state', "ok", { qos: 1, retain: true });

			//发送
			//client.end();
			//发送完后立即结束此次和服务端建立的请求
		});

		client.on('message', function(topic, message) {
			//console.log( topic );
			//console.log( message.toString() );
			var spl = topic.split("/");
			var type = spl[spl.length-1];
			var mess = message.toString();
			switch (type) {
				case 'nav':
					my_mqtt.navigat(mess);
					break;
				case 'info':
					my_mqtt.tishiText(mess);
					break;
				case 'admin':
					my_mqtt.Admin(mess);
					break;
				default :
				break;
			}
		});
	},
	//导航
	navigat: function( json ){
		//创建窗口
		var create_win = function(){
			var childWin = new BrowserWindow({parent: my_mqtt.mainWindow, modal: true, show: false,frame: false,transparent: true})
			childWin.once('ready-to-show',() => {childWin.show()})
			return childWin
		}

		var close_win = function(){
			if( !my_mqtt.childWin.isDestroyed() ){
				my_mqtt.childWin.close();
			}
		}

		//console.log( typeof(json) );
		try {
			var nav_json = JSON.parse( json );
			if(typeof(nav_json)=='object'){
				if ( nav_json.event == 'open'){
					var rx=/^https?:\/\//i;
					var url = nav_json.url;
					if(!rx.test(url)) url = "file:///"+__dirname+"/html/"+ url;
					url = url.replace(/\\/g, '/');

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
				if (nav_json.event == 'close'){
					if (typeof(this.childWin) == 'object'){
						close_win()
					}
				}
			}
		}catch(err){
			console.log("err:"+err);
		}
	},
	//提示文字
	tishiText: function( json ){
		var tsjson = {"tishitext": json };
		my_mqtt.mainWindow.webContents.send('public',tsjson);
	},
	//管理
	Admin: function( mess ){
		if (!mess) return;
		try {
			var mess_json = JSON.parse( mess );
			if(typeof(mess_json)=='object'){
				if (mess_json['receive']=='equipm'){
					var body_str = JSON.stringify( mess_json['body']);
					var childSync = process.execSync( config.pythonapi +'admin '+ escape(body_str).toString() );
					console.log( childSync.toString() );
				}
			}
		}catch(err){
			console.log(err);
		}
	}
}

module.exports = my_mqtt;