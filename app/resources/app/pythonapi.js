const process = require('child_process');
const config = require('./config');

var pythinapi = {
	//执行
	run : function( runtype ){
		try{
			var restr = process.execSync( config.pythonapi + runtype);
			return restr.toString();
		}catch(err){
			return ''
		}
	}
}

module.exports = pythinapi;