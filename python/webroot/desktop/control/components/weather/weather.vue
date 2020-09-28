<template>
  <div id="weather-box">
    <!-- 晴 阴 晴 雨 雾 雪 -->
    <div class="head weather-today">
      <div :class="['now-weather', 'ico_104']"></div>
      <div class="title">
        <div>
          <span style="font-size: 18">{{basic.location}}</span>
          <span class="select-btn" @click="setLocation">切换</span>
        </div>
        <div>
          <span class="msg">{{now.cond_txt}}</span>
          <span>{{now.tmp}}°C</span>
        </div>
      </div>
    </div>

    <div class="foot">
      <div class="tomorrow">
        <h3>明天</h3>
        <div :class="['weather-icon',tomorrowIco]"></div>
        <div class="day-info">
          <i class="temperature">{{daily_forecast[0].tmp_min}}°C&nbsp;</i>
          <i>{{daily_forecast[0].cond_txt_d}}</i>
        </div>
      </div>

      <div class="after-tomorrow">
        <h3>后天</h3>
        <div :class="['weather-icon',afterTomorrowIco]"></div>
        <p class="day-info">
          <i class="temperature">{{daily_forecast[1].tmp_min}}°C&nbsp;</i>
          <i>{{daily_forecast[1].cond_txt_d}}</i>
        </p>
      </div>
      <div id="after-three-days">
        <h3>大后天</h3>
        <div :class="['weather-icon',thirdDaysIco]"></div>
        <div class="day-info">
          <i class="temperature">{{daily_forecast[2].tmp_min}}°C&nbsp;</i>
          <i>{{daily_forecast[2].cond_txt_d}}</i>
        </div>
      </div>
    </div>

    <el-dialog title="选择城市" :visible.sync="dialogVisible" width="30%">
      <el-cascader
        v-model="value"
        :options="citys"
        @change="handleChange"
        placeholder="请选择城市"
        style="width: 100%"
      ></el-cascader>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
var api = import('/desktop/control/api/index.js')
var citys = import('/desktop/control/components/weather/js/citydata.js')
// import citydata from "./js/citydata";

module.exports = {
  data() {
    return {
      // 当天天气图标
      todayIco: '',
      // 明天天气图标
      tomorrowIco: '',
      // 后天天气图标
      afterTomorrowIco: '',
      // 大后天天气图标
      thirdDaysIco: '',

      timer: '',

      // 天气数据
      basic: {
        admin_area: '',
        cid: '',
        cnty: '',
        lat: '',
        location: '',
        lon: '',
        parent_city: '',
        tz: '',
      },
      now: {
        // 天气
        cond_txt: '',
        // 体感温度
        fl: '',
        // 湿度
        hum: '',
        // 温度
        tmp: '',
        wind_dir: '',
        wind_sc: '',
      },
      // 未来天气预报
      daily_forecast: [
        {
          cond_code_d: '',
          cond_code_n: '',
          cond_txt_d: '',
          cond_txt_n: '',
          date: '',
          hum: '',
          mr: '',
          ms: '',
          pcpn: '',
          pop: '',
          pres: '',
          sr: '',
          ss: '',
          tmp_max: '',
          tmp_min: '',
          uv_index: '',
          vis: '',
          wind_deg: '',
          wind_dir: '',
          wind_sc: '',
          wind_spd: '',
        },
        {
          cond_code_d: '',
          cond_code_n: '',
          cond_txt_d: '',
          cond_txt_n: '',
          date: '',
          hum: '',
          mr: '',
          ms: '',
          pcpn: '',
          pop: '',
          pres: '',
          sr: '',
          ss: '',
          tmp_max: '',
          tmp_min: '',
          uv_index: '',
          vis: '',
          wind_deg: '',
          wind_dir: '',
          wind_sc: '',
          wind_spd: '',
        },
        {
          cond_code_d: '',
          cond_code_n: '',
          cond_txt_d: '',
          cond_txt_n: '',
          date: '',
          hum: '',
          mr: '',
          ms: '',
          pcpn: '',
          pop: '',
          pres: '',
          sr: '',
          ss: '',
          tmp_max: '',
          tmp_min: '',
          uv_index: '',
          vis: '',
          wind_deg: '',
          wind_dir: '',
          wind_sc: '',
          wind_spd: '',
        },
      ],

      dialogVisible: false,

      // 级联学则器
      value: [],
      citys: '',
    }
  },
  computed: {},
  created() {
    this.getWeather()
    this.timer = setInterval(this.updateWeatherInfo, 30 * 60 * 1000)
    this.setCitydata()
  },
  methods: {
    //获取天气
    getWeather() {
      var _this = this
      axios
        .get('/api/mojing.py', { params: { op: 'getweather' } })
        .then(function (response) {
          // console.log("axios-responese", response.data);
          _this.basic = response.data.basic
          _this.now = response.data.now
          _this.daily_forecast = response.data.daily_forecast

          // 设置天气图标
          _this.setClass(
            _this.now.cond_code,
            _this.daily_forecast[0].cond_code_d,
            _this.daily_forecast[1].cond_code_d,
            _this.daily_forecast[2].cond_code_d
          )
        })
    },

    // 设置天气图标类名
    setClass(todayIco, tomorrowIco, afterTomorrowIco, thirdDaysIco) {
      this.todayIco = 'ico_' + todayIco
      this.tomorrowIco = 'ico_' + tomorrowIco
      this.afterTomorrowIco = 'ico_' + afterTomorrowIco
      this.thirdDaysIco = 'ico_' + thirdDaysIco
    },

    // 更新天气数据
    updateWeatherInfo() {
      var d = new Date()
      var hours = d.getHours()
      var minutes = d.getMinutes()
      // console.log(hours, ":", minutes);

      if (hours === 0 && minutes === 0) {
        console.log('updateWeatherInfo')
        this.getWeather()
      }
    },

    // 更换地区
    setLocation() {
      this.dialogVisible = true
    },

    handleChange(value) {
      console.log(value)
    },

    // 设置省市区数据
    setCitydata() {
      citys.then((res) => {
        // console.log("城市数据", res.default);
        this.citys = res.default
      })
    },
  },

  // 销毁DOM元素时
  beforeDestroy() {
    clearInterval(this.timer)
  },
}
</script>


<style scoped>
@import './css/myweather_ico.scss';

#weather-box {
  width: 100%;
  height: 100%;
}

.weather-today {
  display: flex;
  width: 100%;
  height: 45%;
  border-bottom: 1px solid #fff;
  background-color: #aa95d3;
}

.now-weather {
  width: 40%;
  height: 100%;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 80%;
}

.title {
  width: 60%;
}

.title > div {
  width: 100%;
  height: 50%;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}

.title > div:first-child {
  border-bottom: 1px solid #666;
}

.title span {
  color: #fff;
}

.title .msg {
  font-size: 20px;
  font-weight: 580;
}

.foot {
  width: 100%;
  height: 55%;
  display: flex;
  color: rgb(223, 221, 221);
}

.foot > div {
  width: 33.4%;
  height: 100%;
  text-align: center;
}

.foot > div > h3 {
  height: 30%;
  font-size: 14px;
  font-weight: 400;
  /* color: #fff; */
  background-color: #aa95d3;
  display: flex;
  align-items: center;
  justify-content: center;
}

.weather-icon {
  width: 100%;
  height: 40%;
  /* background-color: #6699cc; */
  background-color: #aa95d3;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 37%;
}

.last-icon {
  border: none;
}

.day-info {
  height: 30%;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #6699cc;
}

.select-btn {
  color: green !important;
  cursor: pointer;
}
</style>
