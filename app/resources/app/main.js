const {app,BrowserWindow} = require('electron');
const control = require('./control');

var mainWindow = null;

//自定义调试函数
console = {win:'',log:function(str){this.win.webContents.send('console',str);}}

app.on('window-all-closed', function() {
	if (process.platform != 'darwin') {
		app.quit();
	}
});

app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');

app.on('ready', function() {
	//隐藏菜单栏
	//electron.Menu.setApplicationMenu(null);

	var shared = {argv: process.argv}
	var options = {width: 1024,height: 630}
	if (shared.argv.length > 1){
		if (shared.argv[1]=='Debug'){
			options = {
				backgroundColor: '#000000',
				width: 1024,
				height: 630
			}
		}
	}else{
		options = {
			backgroundColor: '#000000',
			width: 1,
			height: 1,
			webPreferences:{devTools: false},
			kiosk: true	//全屏模式
		}
	}

	// 创建浏览器窗口。
	mainWindow = new BrowserWindow(options);
	mainWindow.openDevTools();// 打开开发工具

	console.win = mainWindow;

	// 加载应用
	control.Init(mainWindow);

	// 当mainWindow被关闭，这个事件会被发出
	mainWindow.on('closed', function() {mainWindow = null;});
});
