/**
 * 全局JS，网络状态，显示提示文字
**/
var html = '<div class="top_status" id="statusbar"><span class="iconfont" id="network"></span></div><div id="tishiText"></div>';
$(function(){
	if (!$('#statusbar').length){$('.main-body').append(html);}

	var network = $('#network');		// 网络状态
	var tishiText = $('#tishiText');

	//==================麦的状态动画=========================
	var mic_state = {
		Init: function(){
			this.canvas = document.getElementById('canvas');
			this.ctx = canvas.getContext('2d');
			this.canvas.width = 80;
			this.canvas.height = 80;
			this.radius = 15;
			this.timer = 0;
			this.is_up_do = '';
			return this;
		},
		drawCircle : function() {
			this.ctx.beginPath();
			this.ctx.arc(40, 40, this.radius, 0, Math.PI * 2); //划弧
			this.ctx.closePath();
			this.ctx.lineWidth = 3;
			this.ctx.strokeStyle = 'rgba(38, 147, 255,1)';
			this.ctx.stroke();

			this.radius += 0.5;
			if ( this.radius > 30) {
				this.radius = 0;
			}
		},
		render: function(){
			var prev = this.ctx.globalCompositeOperation;
			this.ctx.globalCompositeOperation = 'destination-in';
			this.ctx.globalAlpha = 0.80;
			this.ctx.fillRect(0, 0, canvas.width, canvas.height);
			this.ctx.globalCompositeOperation = prev;
			this.drawCircle();
		},
		up_staut: function(){
			var timer2 = setInterval(function() {
				mic_state.render()
				if ( mic_state.radius==0){window.clearInterval(timer2);}
			}, 20);
		},
		do_staut: function(){
			this.radius = 15
			this.render()
		},
		main: function( st ){
			var newst = parseInt(st)
			if ( newst == 0 ){
				if ( this.is_up_do != newst) this.do_staut()
			}else{
				if ( this.is_up_do != newst || this.radius==0) this.up_staut()
			}
			this.is_up_do = newst
		}
	};
	//====================END==========================

	var micstate = mic_state.Init();

	//接收主进程消息
	var timer1 = 0
	require('electron').ipcRenderer.on('public',function(event, json){
		//麦的状态
		if ( json.type=='mic' ){
			if ( json.state == 'start'){$('#micro').show();}
			if ( json.state == 'stop'){$('#micro').hide();}
			if ( json.state=='1' || json.state=='0'){
				micstate.main( json.state );
			}
		}

		//设备状态
		if (json.type=='dev'){
			if (json.netstatus==1){
				network.html('&#xe6ae;');
			}else{
				network.html('&#xe726;');
			}
		}

		//语音消息提示
		if (json.type=='text'){
			var json_obj = json;		//JSON.parse(json.tishitext);

			var msg = json_obj.msg;
			var timer = json_obj.timer * 1000;

			if(json_obj.init==1) $('#tishiText').empty();

			var ts_arr = $('#tishiText div');

			if (ts_arr.length >= 4){
				ts_arr.first().remove();
				$('#tishiText div').eq(0).css({'opacity':'0.1'});
				$('#tishiText div').eq(1).css({'opacity':'0.3'});
			}

			var duihua = '<div class="'+ json_obj.obj +'">'+msg+'</div>';

			$('#tishiText').append(duihua);

			window.clearTimeout(timer1);
			timer1 = setTimeout(function(){$('#tishiText').empty();},30000);
		}
	});
});

//加载动画
$(window).load(function(){$("#loading").fadeOut(500);});
