var process = require('child_process');
var http = require("http");		//引入http模块
const url = require("url");
const path = require("path");
const fs = require("fs");
var querystring = require('querystring');
var qr = require('./my_modules/qr-image');

//配网
var set_wifi = {
	mainWindow:'',		// 窗口对象
	web_server:'',		// web 服务器
	serverip: '10.0.0.1',
	wifi_name: 'HTTP_10_0_0_1_8088',	// wifi 名称
	port: 8088,
	root: './config_net',
	create_ap: config.rootpath + 'python/bin/create_ap',
	ctime: 0,			// 查询热点开启状态定时器
	is_exit: false,		// 是否退出查询

	ctime_clist: 0,		// 查询连接热点客户端定时器

	ctime_i: '',		// 检测网络状态定时器次数
	ctime_erri: 0,		// 连接失败重试次数

	//查询连接到热点的客户端
	query_ap_clients: function(webContents){
		var childSync = process.execSync('sudo '+ set_wifi.create_ap + ' --list-clients wlan0');
		var retstr = childSync.toString();

	    var regExp = /MAC\s+IP\s+Hostname/g;
	    var res = regExp.exec(retstr);
	    if (res){
		    //有客户端连接
	    	webContents.executeJavaScript(`$(".two").show()`);
    	}else{
	    	webContents.executeJavaScript(`$(".two").hide()`);
    	}
	},

	//打开配网网页
	open_web: function(){
		set_wifi.mainWindow.loadURL("http://"+set_wifi.serverip+":"+set_wifi.port+"/server.html");
		var webContents = set_wifi.mainWindow.webContents;
		set_wifi.ctime_clist = setInterval(function(){
			set_wifi.query_ap_clients(webContents);
		},2000);
	},
	mine: {
		"css": "text/css",
		"gif": "image/gif",
		"html": "text/html",
		"ico": "image/x-icon",
		"jpeg": "image/jpeg",
		"jpg": "image/jpeg",
		"js": "text/javascript",
		"json": "application/json",
		"pdf": "application/pdf",
		"png": "image/png",
		"svg": "image/svg+xml",
		"swf": "application/x-shockwave-flash",
		"tiff": "image/tiff",
		"txt": "text/plain",
		"wav": "audio/x-wav",
		"wma": "audio/x-ms-wma",
		"wmv": "video/x-ms-wmv",
		"xml": "text/xml"
	},
	//创建web服务器
	create_server: function(){
		if( this.web_server.listening ){
			//console.log('Web服务器已运行');
			set_wifi.open_web();
		}else{
			this.web_server = http.createServer((request,response) => {
			    var pathname = url.parse(request.url).pathname;
			    //console.log( pathname );

			    //手机设置二维码
			    if (pathname =='/setqr'){
				    var set_url = "http://"+set_wifi.serverip+":"+set_wifi.port+"/";
					var code = qr.image(set_url, { type: 'png' });
					response.setHeader('Content-type', 'image/png');  //sent qr image to client side
					code.pipe(response);
					return;
				};

				//获取WfFi列表
				if (pathname =='/getwifilist'){
					clearTimeout(set_wifi.ctime_clist);
					var str = this.get_wifilist();
					response.writeHead(200, {'Content-Type': 'text/plain'});
					response.end(str);
					return;
				}

				//设置WiFi
				if (pathname =='/setwifi'){
					if( request.method =='POST'){
						var data = '';
				        request.on('data', function(chunk){data += chunk;});
				        request.on('end',function(){
				            data = decodeURI(data);
				            var json = querystring.parse(data);
				            set_wifi.set_wifinet(response, json );
				        });
			        }
					return;
				}

				if (pathname == "/favicon.ico") {return;}	//去除无效的信息
				if (pathname == "/") pathname = "/index.html";

			    var realPath = path.join(__dirname, this.root, pathname);

			    var ext = path.extname(realPath);
			    ext = ext ? ext.slice(1) : 'unknown';
			    fs.exists(realPath, function (exists) {
			        if (!exists) {
			            response.writeHead(404, {'Content-Type': 'text/plain'});
			            response.write("404 not found " + pathname);
			            response.end();
			        } else {
			            fs.readFile(realPath, function (err, file) {
			                if (err) {
			                    response.writeHead(500, {'Content-Type': 'text/plain'});
			                    response.end(err);
			                } else {
			                    var contentType = set_wifi.mine[ext] || "text/plain";
			                    response.writeHead(200, {'Content-Type': contentType});
			                    response.write(file);
			                    response.end();
			                }
			            });
			        }
			    });
			});
			this.web_server.listen(set_wifi.port,function(){
			    //console.log('Web服务器运行');
			    set_wifi.open_web();
			});
		}
	},

	// 获取WiFi列表
	get_wifilist: function(){
		try {
			var childSync = process.execSync('sudo iwlist wlan0 scan | grep -E "ESSID|Quality|IEEE"');
			var retstr = childSync.toString();
			var res = retstr.split("Quality");

		    var re_name = /ESSID:"(.+)"/g
		    var re_pass = /IE:\s+IEEE\s+(.+)\s+Version/g
		    var re_qual = /\=(\d+)\/\d+/g

		    var list = [];
		    res.forEach(function(v,i,a){
		        var vv = v.split("\n");
		        var line_arr = {};
		        vv.forEach(function(n){
			        var wifi_name = re_name.exec(n);
			        if (wifi_name) line_arr.wifi_name = wifi_name[1];
			        var wifi_pass = re_pass.exec(n);
			        if (wifi_pass) line_arr.wifi_pass = wifi_pass[1];
			        var wifi_qual = re_qual.exec(n);
			        if (wifi_qual) line_arr.wifi_qual = wifi_qual[1];
		        })
		        if (line_arr.wifi_name) list.push(line_arr);
		        line_arr = null;
			});
			return JSON.stringify(list);
		} catch (ex) {
			return "{}";
		}
	},

	loop_test:function(webContents){
		try {
			var childSync = process.exec('sudo wpa_cli status',function (error, stdout, stderr) {
				var retstr = stdout.toString();
				var ap_arr = {};
				var strAry = retstr.split(/\n/);
				for (i = 0; i < strAry.length; i++) {
				    if (strAry[i].indexOf('=')>0){
					    var n = strAry[i].split('=');
					    ap_arr[n[0]] = n[1];
					}
				}

				if ( ap_arr.wpa_state=='COMPLETED' && ap_arr.ip_address !=''){
					process.execSync('sudo '+ config.pythonapi +' setnewdev 0');				// 设置新设备为：0
					webContents.executeJavaScript(`$("#st_text").html("连接成功！")`);
					webContents.executeJavaScript(`$("#end_text").html("系统将在3秒钟后进入首页")`);
					set_wifi.web_server.close();		// 关闭Web服务
					setTimeout(function(){
						process.exec('sudo reboot');		//重启系统
						//set_wifi.mainWindow.loadURL("file://"+__dirname+"/html/index.html");
					},2000);
					return ;
				}else if ( ap_arr.wpa_state=='SCANNING'){
					webContents.executeJavaScript(`$("#st_text").html("连接失败！正在重试……，请稍候！")`);
					set_wifi.ctime_erri++;
					if (set_wifi.ctime_erri > 10){
						webContents.executeJavaScript(`$("#st_text").html("正在返回重新设置连网")`);
						set_wifi.stop_ap();
						return;
					}
				}else{
					set_wifi.ctime_i = set_wifi.ctime_i +'.';
					if (set_wifi.ctime_i.length > 8 ) set_wifi.ctime_i = '.';
					webContents.executeJavaScript('$("#st_text").html("正在连接'+set_wifi.ctime_i+'，请稍候！")');
					webContents.executeJavaScript(`$("#end_text").html("如果长期处于正在连接状态，请关闭设备重启。")`);
				}

				set_wifi.ctime = setTimeout(function(){
					set_wifi.loop_test(webContents);
				},3000);
			});
		}catch(ex) {
			//return ;
		}
	},

	//检测网络状态
	test_netstatus: function(){
		set_wifi.mainWindow.loadURL("http://"+set_wifi.serverip+":"+set_wifi.port+"/server_netstatus.html");
		var webContents = set_wifi.mainWindow.webContents;
		set_wifi.loop_test( webContents )
	},

	// 设置WiFi网络
	set_wifinet: function( response, postjson ){
		response.writeHead(200, {'Content-Type': 'text/plain'});
		if (postjson.wifiname != ''){
			this.test_netstatus();		//检测网络状态
			var json_str = JSON.stringify(postjson);
			process.exec("sudo "+ config.pythonapi +" set_wifi '"+ escape(json_str).toString() +"'");
			response.write('OK');
		}else{
			response.write('Error');
		}
		response.end();
		return;
	},

	//查询
	query_ap:function(){
		var cmd = set_wifi.create_ap;
	    var curl = process.spawn('sudo',[cmd,'--list-running']);
	    // 为spawn实例添加了一个data事件
	    var fdata = '';
	    curl.stdout.on('data', function(data) {fdata += data;});
	    // 添加一个end监听器来关闭文件流
	    curl.stdout.on('end', function(data) {
		    var regExp = /(\d+)\s+wlan0/g;
		    var res = regExp.exec(fdata);
		    if (res){
			    //开启成功
		    	clearTimeout(set_wifi.ctime);
		    	set_wifi.is_exit = true;
		    	set_wifi.create_server();
	    	}
	    });
	      // 当子进程退出时，检查是否有错误，同时关闭文件流
	    curl.on('exit', function(code) {
			if (!set_wifi.is_exit){
				set_wifi.ctime = setTimeout(function(){set_wifi.query_ap();},1000)
			}else{
				clearTimeout(set_wifi.ctime);
			}
     	});
	},
	//开启热点
	start_ap: function(){
		var cmd = 'sudo '+ set_wifi.create_ap + ' -n --no-virt --redirect-to-localhost -g'+ set_wifi.serverip +' wlan0 '+ set_wifi.wifi_name;
		//console.log( cmd );
		process.exec( cmd );
    },
    stop_ap: function(){
	    this.ctime = 0;				// 定时器
		this.is_exit = false;		// 是否退出查询
		this.ctime_i = '';			// 检测网络状态定时器次数
		this.ctime_erri = 0;		// 连接失败重试次数
	    //kill 掉所有 create_ap 进程
	    var curl = process.spawn('sudo', [config.pythonapi,'init_ap']);
	    var fdata = '';
	    curl.stdout.on('data', function(data) {fdata += data;});
	    curl.stdout.on('end', function(data) {
		    //console.log('data: ' + data);
	    });
	    curl.on('exit', function(code) {
		    //console.log('set_wifi->stop_ap: ' + code);
		    set_wifi.start_ap();
		    set_wifi.query_ap();
     	});
    },
    init: function(mainWindow){
	    this.mainWindow = mainWindow;
	    this.stop_ap();
    }
};

module.exports = set_wifi;