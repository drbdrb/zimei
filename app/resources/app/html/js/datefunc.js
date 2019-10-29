const pythonapi = require('../pythonapi');

//天气
var weather = {
	weat_type: {
		'comf':{'name':'舒适度指数','level':['舒适','较舒适','较不舒适','很不舒适','极不舒适','不舒适','非常不舒适']},
		'cw':{'name':'洗车指数','level':['适宜','较适宜','较不宜','不宜']},
		'drsg':{'name':'穿衣指数','level':['炎热','热','舒适','较舒适','较冷','冷','寒冷']},
		'flu':{'name':'感冒指数','level':['少发','较易发','易发','极易发']},
		'sport':{'name':'运动指数','level':['适宜','较适宜','较不宜']},
		'trav':{'name':'旅游指数','level':['适宜','较适宜','一般','较不宜','不适宜']},
		'uv':{'name':'紫外线指数','level':['最弱','弱','中等','强','很强']},
		'air':{'name':'空气污染指数','level':['优','良','中','较差','很差']},
		'ac':{'name':'空调开启指数','level':['长时间开启','部分时间开启','较少开启','开启制暖空调']},
		'ag':{'name':'过敏指数','level':['极不易发','不易发','较易发','易发','极易发']},
		'gl':{'name':'太阳镜指数','level':['不需要','需要','必要','很必要','非常必要']},
		'mu':{'name':'化妆指数','level':['保湿','保湿防晒','去油防晒','防脱水防晒','去油','防脱水','防晒','滋润保湿']},
		'airc':{'name':'晾晒指数','level':['极适宜','适宜','基本适宜','不太适宜','不宜','不适宜']},
		'ptfc':{'name':'交通指数','level':['良好','很好','一般','较差','很差']},
		'fsh':{'name':'钓鱼指数','level':['适宜','较适宜','不宜']},
		'spi':{'name':'防晒指数','level':['弱','较弱','中等','强','极强']}
	},
	lifestyle:[],		// 生活指数
	life_i: 0,			// 指数显示当前
	//获取城市数据
	get_city: function( callfunc ){
		try{
			var isnew = pythonapi.run('get_city');
			if (isnew !='' ){
				var json = JSON.parse(isnew.toString());
				if( json ){
					var city = json.city;
					var city_cnid = json.city_cnid;
					callfunc( city, city_cnid );
				}
			}
		}catch(err){
			console.log(err);
		}
	},
	//变幻生活指数
	bianhuanzs: function(){
		var life_len = weather.lifestyle.length;
		var life_html = '';
		var life_obj = $('#life_index');
		for(var i=0;i<life_len;i++){
			var life_n = weather.lifestyle[ i ];
			var type = life_n['type'];
			var brf  = life_n['brf'];
			var weat_type = weather.weat_type[type];
			life_html += '<dl><dt>'+ weat_type['name'] +'</dt><dd>';

			//当前html根字体大小 == px 值
			html_size = parseInt($('html').css("font-size"));

			var level = weat_type['level'];
			bfb = level.indexOf(brf) + 1;

			bfb = parseInt((bfb/level.length) * 100);		//百分比
			bfb_w = html_size * 4;							//初始化几个rem
			obj_w = parseInt((bfb_w * bfb)/100);			//图表宽度

			//定义颜色
			obj_bg_r = parseInt((255 * bfb)/100);
			obj_bg_g = 255 - parseInt((255 * bfb)/100);
			rgb = 'rgb('+ obj_bg_r +','+ obj_bg_g +',0)';

			life_html += '<ul><li class="brf_len" style="width:'+obj_w+'px;background-color:'+ rgb +'"></li><li class="brf_text">'+ brf +'</li></ul>';
			life_html += '</dd></dl>';
		}

		life_obj.html( life_html )
	},
	//设置HTML显示
	set_html: function( data ){
		if (weather.timer) window.clearTimeout(weather.timer);
		//城市信息
		var cityInfo = data.basic;
		$('#city_name').text( cityInfo.location );

		//实时天气
		var live = data.now;
		var update = data.update.loc;
		update = update.split(' ');
		$('#uptime').text( '('+update[1]+')更新');			// 更新时间

		$('#tq_ico').removeClass().addClass('ico_'+live.cond_code);

		$('#tianqi').text(live.cond_txt);	// 天气情况
		$('#tg_tigang').text(live.fl);		// 体感
		$('#sw_wendu').text(live.tmp);		// 温度
		$('#sw_shidu').text(live.hum);		// 相对湿度
		$('#wind_dir').text(live.wind_dir)
		$('#wind_sc').text(live.wind_sc + '级')


		//生活指数
		//console.log( data.lifestyle );
		weather.lifestyle = data.lifestyle;
		//weather.lifestyle[0]['brf'] = '非常不舒适'
		weather.bianhuanzs();

		//逐小时
		var hourly = data.hourly;
		var dt_html = '';
		$.each(hourly, function(i, n){
			var n_time_obj = new Date(Date.parse(n.time.replace(/-/g, "/")));
			var dl = '<div class="hh"><ul><li>'+n_time_obj.getHours()+'点</li>';
		    dl += '<li class="weatico"><i class="ico_'+n.cond_code+'"></i></li>';
		    dl += '<li>'+n.tmp+'°</li></ul></div>';
			dt_html += dl;
		});
		$('#hourly').html(dt_html);

		//多天
		var forecast = data.daily_forecast;
		var dt_html = '';
		$.each(forecast, function(i, n){
			var high = n.tmp_max;
			var low = n.tmp_min;
			var icod = 'ico_' + n.cond_code_d;
			var icon = 'ico_' + n.cond_code_n;
			var cond_d = n.cond_txt_d;
			var cond_n = n.cond_txt_n;
			var n_date = n.date;
			var n_date_obj = new Date(Date.parse(n_date.replace(/-/g, "/")));
			var this_date = dateclass.daily_date[n_date_obj.getDate()];
			var dl = '';
			if ( this_date != undefined ){
				var week = dateclass.weeks[ this_date.week ];
				var date_text = this_date.call;

				dl = '<dl><dt>'+date_text+' <span>(周'+ week +')</span></dt><dd class="weatico"><i class="'+icod+'"></i><i class="'+icon+'"></i>';
				dl += '<ul><li>'+low+'° ~ '+high+'°</li></ul></dd></dl>';
			}
			dt_html += dl;
		});
		$('#doutian').html(dt_html);
	},
	Init: function(){
		var chinese_date = ['今天','明天','后天'];
		var _this = this;

		this.get_city(function(city, cnid){
			var apiurl = config.httpapi + '/Raspberry/getweather.html';
			var postdata = {'cnid':cnid,'city':city};
			$.ajax({
				url: apiurl,
				type: "POST",
				data: postdata,
				dataType: "json",
				success: function(data) {
					//console.log( data );
					if (data){
						try{
							_this.set_html(data)
						}
						catch(err){
						   	//在此处理错误
						   	setTimeout(function(){
							   	_this.set_html(data)
							},1000);
						}
					}
				}
			});
		})
	}
}

//日历
var dateclass = {
	is_re_date: true,	// 是否刷新日期
	is_re_time: true,	// 是否刷新时，分
	//weather_init: true,	// 首次初始化天气数据
	weeks : ["日","一","二","三","四","五","六"],
	chinese_date : ['今天','明天','后天'],
	daily_date: {},		// 日常 日期称呼
	// 补零
	buling: function(s){
		return s < 10 ? '0' + s: s;
	},
	numtochi: function(s){
		var chnNumChar = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九"];
		var numarr = s.toString();
		var newstr = '';
		for(var i=0;i<10;i++){
			numarr = numarr.replace(i,chnNumChar[i]);
		}
		return numarr;
	},
	// 显示日期
	date_show: function( json ){
		$('#year').text(json.year);
		if (json.month==1) json.month = '元';
		$('#month').text(json.month);
		$('#date').text(json.date);
		$('#week').text(json.week);
	},
	//运算日常称呼时间
	daily_func: function( myDate, i ){
		var date = myDate.getDate();     	// 获取当前日
		var week = myDate.getDay();			// 获取星期
		var call_text = this.chinese_date[i] ? this.chinese_date[i] : date +'日';
		this.daily_date[ date.toString() ] = {'week':week,'call': call_text };
		var d = new Date(myDate);
		myDate.setDate( date + 1 );
		i++;
		if (i>6) return;
		this.daily_func( myDate, i );
	},
	//日期
	now_date: function(){
		var myDate = new Date();
	    var year   = myDate.getFullYear(); 	// 获取当前年
	    var month  = myDate.getMonth()+1; 	// 获取当前月
	    var date   = myDate.getDate();     	// 获取当前日
	    var week   = '星期' + this.weeks[myDate.getDay()];
	    this.daily_func( myDate, 0 );
	    this.date_show({year: year,month: month,date: date,week: week});
	    this.is_re_date = false;
	},
	// 农历显示
	nongli_show: function(){
		$.ajax({
			url: config.httpapi + "/Raspberry/laohuangli.html",
			type: "GET",
			dataType: "json",
			success: function(data) {
				if (data.reason=='successed'){
					var result = data.result;
					var yinli = result.yinli;
					var yl_arr = yinli.split('月');
					//console.log( result );
					$('#yi').html(result.yi);
					$('#ji').html(result.ji);
					$('#yl_year').html(yl_arr[0]+'月');
					$('#yl_date').html(yl_arr[1]+'日');
				}
			}
		});
	},
	// 时间显示
	time_show: function( json ){
		if (this.is_re_time){
			$('#hours').text( this.buling(json.hours));
			$('#minutes').text( this.buling(json.minutes));
			this.is_re_time = false;
		}
		$('#seconds').text( this.buling(json.seconds));
	},
	now_time: function(){
	    var myDate = new Date();
	    var h = myDate.getHours();		// 获取当前小时数(0-23)
	    var m = myDate.getMinutes();	// 获取当前分钟数(0-59)
	    var s = myDate.getSeconds();
	    if (s==0) this.is_re_time = true;
	    this.time_show({hours: h,minutes: m,seconds: s});

	    if (h==0&&m==0&&s<=1) this.is_re_date = true;
	    if (this.is_re_date){
		    this.now_date();
		    this.nongli_show();
		    weather.Init();
		}
	    if (m==30&&s<=1) weather.Init();
	}
}