const process = require('child_process');
const path = require('path');

const api_path = path.resolve(__dirname,'../../../') + '/python/api.py ';

var pythinapi = {
	//执行
	run : function( runtype ){
		try{
			var restr = process.execSync( api_path + runtype);
			return restr.toString();
		}catch(err){
			return ''
		}
	}
}

module.exports = pythinapi;