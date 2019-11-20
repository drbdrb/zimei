
var config = require('./pythonapi').run('getconfig')
module.exports = JSON.parse( config );