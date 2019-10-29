#!/usr/bin/node

var process = require('child_process');

// -----------------------------测试扫描WiFi----------------------
var set_wifi = require('./set_wifi');
//set_wifi.init('');
//set_wifi.query_ap()

// ------------------------------测试 list-running----------------------
var cmd = '/var/www/server/python/bin/create_ap';
console.log( cmd + ' --list-running');
var curl = process.spawn('sudo',[cmd,'--list-running']);
// 为spawn实例添加了一个data事件
var fdata = '';
curl.stdout.on('data', function(data) {fdata += data;});
// 添加一个end监听器来关闭文件流
curl.stdout.on('end', function(data) {
    console.log('fdata'+fdata.toString() );
    var regExp = /(\d+)\s+wlan0/g;
    var res = regExp.exec(fdata);
    if (res){
	    //开启成功
    	console.log( '开启成功' );
	}
});
  // 当子进程退出时，检查是否有错误，同时关闭文件流
curl.on('exit', function(code) {
    if (code != 0) {console.log('查询退出码:' + code);}
	if (!set_wifi.is_exit){
		//set_wifi.ctime = setTimeout(function(){set_wifi.query_ap();},1000)
	}else{
		clearTimeout(set_wifi.ctime);
		console.log('退出查询');
	}
});