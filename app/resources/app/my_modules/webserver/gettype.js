exports.getextName = function(fs, Extname) { 		//暴露模块的方法getextName，传入fs文件模块，和想更改的文件类型名
	var mes = fs.readFileSync(__dirname+"/mime.json");    //通过文件模块同步的读取方法获取json值
	mes = JSON.parse(mes)[Extname];                 //将获取的值转换为Json对象   
	return mes || "text/html";                      //返回转换的值，如果没有查找成功则返回"text/html"
}