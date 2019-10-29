const http = require("http");	//引入http模块
const fs = require("fs");		//引入fs文件模块
const url = require("url");		//引入url模块
const path = require("path");	//引入path模块
const gettexttype = require(__dirname+"/gettype.js");	//引入自定义模块

var server = {
	port: 80,								//端口
	root: __dirname+'/html',				//网站目录
	serverobj:'',
	start: function(port=80,root=''){
		var port = port ? port : 80;
		var root = root ? root : this.root;
		this.port = port;
		this.root = root;
		this.serverobj = http.createServer((req, res) => {										//创建服务器
			var urls = req.url;													//获取地址栏用户输入的信息
			urls = url.parse(urls).pathname;									//通过输入信息截取相关路径信息
			console.log(urls);
			var urlstype = gettexttype.getextName(fs, path.extname(urls));		//获取文件的后缀名并调用自定义模块更改信息
			if (urls != "/favicon.ico") {										//去除无效的信息
				if (urls == "/") {												//判断是否只输入了域名，如果是则更改为index页面
					urls = "/index.html";
				} else if (urlstype == "text/html" & urls != "/index.html") {	//如果为网页且不是主页，则路径应该在html文件夹下
					urls = urls;
				}
				fs.readFile( root +'/'+ urls, (err, data) => {
					if (err) {
						fs.readFile( root + "/404.html", (err, nodata) => {		//查找不到网页，打开404页面
							res.writeHead(404, {"content-type": "" + urlstype + ";charset='utf-8'"}); 												//编写头部信息
							res.write(nodata);									//将404页面内容填入页面
							res.end();											//关闭刷新
						})
						return;													//阻止程序继续往下运行
					}
					res.writeHead(200, {
						"content-type": "" + urlstype + ";charset='utf-8'"
					});															//编写头部信息
					res.write(data);											//将获取的网页内容写入
					res.end();													//关闭
				})
			}
		});
		this.serverobj.listen(port,function(){
		    console.log('WEB服务已启动\n端口:'+port+'\n网站目录：'+root);
		});
	},
	stop: function(){
		this.serverobj.close();
	}
}

module.exports = server;