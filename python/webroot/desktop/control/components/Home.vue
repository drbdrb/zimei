<template>
  <div>
    <!-- 导航栏 -->
    <el-row class="nav-bar">
      <el-col :span="14">
        <!-- <title /> -->
        <systemtitle :sys-title="configInfo.VIEW.title" />
      </el-col>

      <el-col :span="19" class="icon-container">
        <!-- <div @click="wifiDrawer = true"> -->
        <div @click="wifiClick">
          <!-- wifi图标 -->
          <!-- <wifi :wifi-name="wifiName" /> -->
          <wifi @checkwifi="currentWifi" />
        </div>
        <div @click="drawer = true">
          <!-- 音量图标 -->
          <volume :volume="volumeValue" />
        </div>
      </el-col>
      <el-col :span="1"></el-col>
    </el-row>

    <!-- 第一行 状态信息 -->
    <el-row class="dash-board" type="flex">
      <el-col :span="6">
        <div class="grid-content">
          <div class="status-box">
            <!-- 天气 -->
            <weather class="weather" />
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content">
          <div class="status-box">
            <!-- 日历 -->
            <today />
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content">
          <div class="status-box">
            <!-- 系统开关 -->
            <switch-button :camera="configInfo.CAMERA" />
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content">
          <div class="status-box">
            <!-- 硬件信息 -->
            <hardware ref="hardwareRef" />
          </div>
        </div>
      </el-col>
    </el-row>
    <!-- 插件框 -->
    <el-row>
      <plugin-list />
    </el-row>

    <!-- WIFI-抽屉 -->
    <el-drawer
      :visible.sync="wifiDrawer"
      direction="rtl"
      :with-header="false"
      size="30%"
      :destroy-on-close="true"
    >
      <el-table :data="wifiData" stripe size="mini" style="width: 100%;">
        <el-table-column prop="name"></el-table-column>

        <el-table-column width="80%">
          <template v-slot="scope">
            <el-tag v-if="currentWifiname === scope.row.name" type="success" size="mini">已连接</el-tag>
            <el-button v-else size="mini" @click="dialogHandle(scope.row.name)">连接</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
    <!-- 输入WIFI密码弹窗 -->
    <el-dialog title="请输入WIFI密码" :visible.sync="dialogVisible" width="90%">
      <el-input suffix-icon="iconfont icon-WIFIxinhao-ji" v-model="wifiName" :disabled="true"></el-input>
      <el-input placeholder="点击输入密码" suffix-icon="iconfont icon-mima" v-model="wifiPassWord"></el-input>

      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="connectWifi">确 定</el-button>
      </span>
      <vkeyboard @sendtext="inputPassword" @submit="connectWifi" />
    </el-dialog>
    <!-- 音量-抽屉 -->
    <el-drawer :visible.sync="drawer" direction="rtl" :with-header="false" size="15%">
      <i class="el-icon-message-solid volume-tag">{{ volumeValue }}</i>
      <el-slider v-model="volumeValue" vertical height="250px" :step="5" @change="setVolume"></el-slider>
    </el-drawer>
  </div>
</template>

<script>
// 系统标题
var systemtitle = httpVueLoader('./systemtitle/systemtitle.vue')
// 天气
var weather = httpVueLoader('./weather/weather.vue')
// 日历
var today = httpVueLoader('./today/today.vue')
// 硬件信息
var hardware = httpVueLoader('./hardware/hardware.vue')
// 音量
var volume = httpVueLoader('./volume/volume.vue')
// wifi信息
var wifi = httpVueLoader('./wifi/wifi.vue')
// 插件列表
var pluginList = httpVueLoader('./pluginList/pluginList.vue')
// 系统开关
var switchButton = httpVueLoader('./switchButton/switchButton.vue')

var vkeyboard = httpVueLoader('./vkeyboard/vkeyboard.vue')

var api = import('/desktop/control/api/index.js')
module.exports = {
  data() {
    return {
      // wifi
      wifiName: '',
      currentWifiname: '',
      wifiDrawer: false,
      wifiData: [],
      // wifi-密码
      dialogVisible: false,
      wifiPassWord: '',

      // 音量
      drawer: false,
      volumeValue: 0,
      // 配置信息
      configInfo: {
        // 摄像头信息
        CAMERA: {
          // enable: true,
          // flip: -1
        },
        // 系统标题
        VIEW: {
          // index: "index.html",
          // path: "desktop/control/",
          // title: "自美魔镜"
        },
      },
      // 硬件信息
    }
  },

  // 页面载入后触
  created() {
    // 获取配置文件-摄像头
    this.fetchConfig()
    // 获取当前音量
    this.getVolumeValue()
    // 获取wifi信息
    this.getWifiList()
    // 检查网络
    // this.checkInternet();
  },

  // 方法
  methods: {
    // 获取配置信息
    fetchConfig() {
      api.then((e) => {
        e.getConfig({ op: 'getconfig' }).then((response) => {
          const data = response.data.config
          this.configInfo.CAMERA = data.CAMERA
          this.configInfo.VIEW = data.VIEW
          // console.log("DATA", response.data);
          // console.log("configInfo.CAMERA", this.configInfo.CAMERA);
          // console.log("configInfo.VIEW", this.configInfo.VIEW);
        })
      })
    },
    // 获取音量
    getVolumeValue() {
      api.then((e) => {
        e.getStatusInfo({ op: 'getVolume' }).then((response) => {
          const data = response.data
          this.volumeValue = data
          // console.log("getVolumeValue", this.volumeValue);
        })
      })
    },
    // 设置音量
    setVolume() {
      // console.log("setVolume", this.volumeValue);
      text = {
        MsgType: 'Text',
        Receiver: 'ControlCenter',
        Data: '音量' + this.volumeValue,
      }
      ZM.send(text)
    },

    // 获取wifi列表
    getWifiList() {
      api.then((e) => {
        e.getStatusInfo({ op: 'wifi_name_list' }).then((response) => {
          const data = response.data
          // console.log("wifi_name_list", data);
          this.wifiData = data.map((item) => {
            return { name: item }
          })
          // console.log("wifiData", this.wifiData);
        })
      })
    },

    // wifi密码弹窗
    dialogHandle(name) {
      api.then((e) => {
        this.wifiName = name
        this.dialogVisible = true
      })
    },

    // 虚拟键盘输入密码
    inputPassword(keyWord) {
      this.wifiPassWord = keyWord
    },

    // 连接wifi
    connectWifi() {
      console.log(
        '连接wifi,name:' + this.wifiName + ',password:' + this.wifiPassWord
      )
      if (this.wifiPassWord === '') {
        console.log("wifiPassWord=''")
      }
      this.sendCommand_wifi_connect(this.wifiName, this.wifiPassWord)
    },

    // 发送连接wifi消息
    sendCommand_wifi_connect(name, password) {
      text2 = {
        MsgType: 'Text',
        Receiver: 'Device',
        Data: {
          action: 'DEVICE_WIFI',
          scanssid: 2,
          wifiname: name,
          wifipass: password,
        },
      }

      text1 = {
        MsgType: 'LoadPlugin',
        Receiver: 'ControlCenter',
        Data: 'Device',
      }
      // console.log("text2", text2);
      // 第二次发送
      ZM.send(text1)
      ZM.send(text2)
    },

    // 打开wifi列表
    wifiClick() {
      this.wifiDrawer = true
      this.getWifiList()
    },

    // 获取当前wifi名
    currentWifi(data) {
      this.currentWifiname = data.trim()
      // console.log("当前wifi名:", this.currentWifiname);
      // console.log(data.trim() === "TP-LINK_DRB", data);
    },
  },

  components: {
    syi,
    pluginList,
    swistemtitle,
    weather,
    today,
    hardware,
    volume,
    wiftchButton,
    vkeyboard,
  },
}
</script>

<style scoped>
.nav-bar {
  height: 50px;
  display: flex;
  align-items: center;
  background-color: rgb(112, 108, 109);
  position: sticky;
  top: 0;
  /* box-shadow: 0 3px 3px rgba(0, 0, 0, 0.3); */
  z-index: 999;
}
.icon-container {
  display: flex;
  justify-content: flex-end;
}
.icon-container div {
  margin-left: 10px;
}
.dash-board {
  margin-top: 15px;
}

.grid-content {
  height: 20vw;
  /* border-radius: 5px; */
  padding: 10px;
}

.status-box {
  width: 100%;
  height: 100%;
  /* box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.3); */
  border: 2px solid rgb(177, 173, 173);
}

.el-slider {
  padding: 0 45%;
}
.el-slider__runway {
  background-color: rgb(174, 179, 179);
}

.volume-tag {
  display: inline-block;
  width: 100%;
  font-size: 25px;
  margin: 40px 0;
  text-align: center;
}

.el-dialog .el-input:first-child {
  margin-bottom: 10px;
}
</style>
