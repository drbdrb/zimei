const rootpath = '/var/www/keyicx/';
module.exports = {
	'mqtt':{
		'server': 'mqtt://mqtt.16302.com:1883',
		'username': '',
		'password': '',
		'clientId': ''
	},
	'screen_size':{			//设置屏幕留白：顶，右，底，左
		'top':'10px',
		'right':'10px',
		'bottom':'10px',
		'left':'10px'
	},
	'rootpath': rootpath,
	'httpapi': 'https://hapi.16302.com',
	'pythonapi': rootpath + 'python/api.py ',
	//不能加sudo 不然摄像头无法启动,py后面必须加空格  因为要接指令
}