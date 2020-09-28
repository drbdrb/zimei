<template>
  <div>
    <i :class="['iconfont', wifiIcon]">&nbsp; :{{wifiName}}</i>
  </div>
</template>

<script>
var api = import('/desktop/control/api/index.js')

module.exports = {
  data() {
    return {
      wifiIcon: 'icon-wangluo',
      timer: '',
      wifiName: '等待连接网络',
    }
  },

  created() {
    // 检查网络
    this.timer = setInterval(this.checkInternet, 3000)
    //
  },

  methods: {
    // 获取wifi名
    getWifiName() {
      api.then((e) => {
        e.getStatusInfo({ op: 'getwifiname' }).then((response) => {
          const data = response.data
          if (data === '') {
            this.wifiName = '有线网络'
            this.wifiIcon = 'icon-youxianwangluo'
            return
          }
          // 无线网络
          // this.wifiName = data.substring(5)
          this.wifiName = data.replace('SSID:', '')
          this.$emit('checkwifi', this.wifiName)
          // 获取当前wifi信号强度
          this.getWifiStrength()
        })
      })
    },

    // 获取当前wifi信号强度
    getWifiStrength() {
      api.then((e) => {
        e.getStatusInfo({ op: 'wifi_strength' }).then((response) => {
          const data = response.data
          if (data === 0) {
            console.log('0')
            return (this.wifiIcon = 'icon-WIFIxinhao-wu')
          }
          switch (data) {
            case 1:
              // console.log('信号强度_1')
              this.wifiIcon = 'icon-WIFIxinhao-ji3'
              break
            case 2:
              // console.log('信号强度_2')
              this.wifiIcon = 'icon-WIFIxinhao-ji2'
              break
            case 3:
              // console.log('信号强度_3')
              this.wifiIcon = 'icon-WIFIxinhao-ji1'
              break
            case 4:
              // console.log('信号强度_4')
              this.wifiIcon = 'icon-WIFIxinhao-ji'
              break

            default:
              // console.log('信号强度_5')
              this.wifiIcon = 'icon-WIFIxinhao-ji'
              break
          }

          // console.log("wifi信号强度", data);
        })
      })
    },

    //检查网络
    checkInternet() {
      api.then((e) => {
        e.getStatusInfo({ op: 'network_detection' }).then((response) => {
          const data = response.data
          // console.log("network_detection", data);

          if (data !== 1) {
            console.log('未联网', data)
            this.wifiIcon = 'icon-wangluo'
            this.wifiName = '未连接网络'
            return
          }

          // console.log("有网络", data);
          this.getWifiName()
        })
      })
    },
  },
  beforeDestroy() {
    setInterval(this.timer)
  },
}
</script>

<style scoped>
i {
  line-height: 50px;
  font-size: 25px;
  height: 50px;
  color: #fff;
}
</style>
