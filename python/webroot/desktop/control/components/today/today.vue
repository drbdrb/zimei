<template>
  <div class="today">
    <div class="day-box">
      <div class="year-month">
        <span>{{year}}-{{month}}</span>
      </div>
      <div class="day">
        <p>
          <span>{{week}}</span>
        </p>
        <div>
          <span>{{day}}</span>
        </div>
        <p>
          <span>{{currentTime}}</span>
        </p>
      </div>
    </div>
    <div class="lunar">
      <span>农历:</span>
      <p>{{nongli}}</p>
    </div>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      timer: '',
      year: '',
      month: '',
      week: '',
      day: '',
      hours: '',
      minute: '',
      secnd: '',
      currentTime: '',

      // 农历
      nongli: '',
    }
  },

  created() {
    this.getYearMonthWeekDay()
    this.getLaoHuangLi()
    this.timer = setInterval(this.updataDaysInfo, 1000)
  },

  methods: {
    // 获取年月日星期
    getYearMonthWeekDay() {
      var d = new Date()
      // 获取年份
      this.year = d.getFullYear()
      // 获取月份
      this.month = d.getMonth() + 1
      if (this.month < 10) {
        this.month = '0' + this.month
      }
      // 获取星期
      this.week = d.getDay()
      var weekName = [
        '星期一',
        '星期二',
        '星期三',
        '星期四',
        '星期五',
        '星期六',
        '星期天',
      ]
      this.week = weekName[this.week - 1]
      // 获取当天
      this.day = d.getDate()
    },

    // 获取当前时间
    getCurrentTime() {
      var d = new Date()
      this.currentTime = d.toLocaleTimeString()
    },

    // 获取农历
    getLaoHuangLi() {
      var _this = this
      axios
        .get('/api/mojing.py', {
          params: {
            op: 'laohuangli',
          },
        })
        .then(function (response) {
          // console.log("axios-responese", response);
          // console.log("response.data.result.yinli", response.data.result.yinli);
          _this.nongli = response.data.result.yinli
          // console.log("nongli:", this.nongli);
        })
        .catch(function (error) {
          console.log('axios-error', error)
        })
    },

    // 更新数据
    updataDaysInfo() {
      var d = new Date()
      var hours = d.getHours()
      var minutes = d.getMinutes()
      var second = d.getSeconds()
      // console.log(hours, ":", minutes, ":", second);
      this.getCurrentTime()
      if (hours === 0 && minutes === 0 && second <= 1) {
        console.log('updataDaysInfo')
        this.getYearMonthWeekDay()
        this.getLaoHuangLi()
      }
    },
  },

  // 销毁DOM元素时
  beforeDestroy() {
    clearInterval(this.timer)
  },
}
</script>

<style scoped>
.today {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.day-box {
  width: 70%;
  height: 75%;
  background-color: #fff;
}

.year-month {
  width: 100%;
  height: 15%;
  font-size: 17px;
  font-weight: 500;
  color: #fff;
  background-color: #eb9f7c;

  display: flex;
  justify-content: center;
  align-items: center;
}

.day {
  width: 100%;
  height: 85%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgb(218, 217, 217);
}
.day > p {
  width: 70%;
  background-color: rgb(218, 217, 217);

  height: 20%;

  display: flex;
  justify-content: center;
  align-items: center;
}

.day p:first-child {
  border-bottom: 1px solid #000;
}

.day p:last-child {
  border-top: 1px solid #000;
}

.day div {
  width: 70%;
  height: 70%;
  background-color: rgb(218, 217, 217);

  font-size: 55px;
  font-weight: 600;

  display: flex;
  justify-content: center;
  align-items: center;
}

.lunar {
  width: 70%;
  height: 15%;
  color: #fff;
  font-size: 12px;
  background-color: #8971f0;

  display: flex;
  justify-content: center;
  align-items: center;
}

.lunar > span {
  color: rgb(212, 241, 206);
}
</style>
