<template>
  <div class="switch-button">
    <div>
      <span>系统设置</span>
    </div>
    <div class="switch-box">
      <!-- 屏幕方向 -->
      <div class="rotate-screen">
        <span>屏幕方向</span>
        <el-select v-model="rotateScreen" size="mini" placeholder="请选择" @change="setScreen">
          <el-option
            v-for="item in screenOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </div>

      <!-- 摄像头方向 -->
      <div class="rotate-camera">
        <span>摄像头方向</span>
        <el-select v-model="camera.flip" size="mini" placeholder="请选择" @change="setCamera">
          <el-option
            v-for="item in cameraOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          ></el-option>
        </el-select>
      </div>

      <!-- 关闭屏幕 -->
      <div class="close-screen">
        <div>
          <el-tag size="small">关闭屏幕</el-tag>
          <el-switch
            v-model="isOn"
            active-color="#13ce66"
            inactive-color="#ff4949"
            @change="screenOff"
          ></el-switch>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var api = import('/desktop/control/api/index.js')

module.exports = {
  data() {
    return {
      isOn: true,

      // 旋转屏幕
      rotateScreen: '-1',
      screenOptions: [
        {
          value: '0',
          label: '默认',
        },
        {
          value: '1',
          label: '旋转90度',
        },
        {
          value: '2',
          label: '旋转180度',
        },
        {
          value: '3',
          label: '旋转270度',
        },
        {
          value: '0x10000',
          label: '左右翻转',
        },
        {
          value: '0x20000',
          label: '上下翻转',
        },
      ],
      // 旋转摄像头
      cameraOptions: [
        { value: 0, label: '上下翻转' },
        { value: 1, label: '左右翻转' },
        { value: -1, label: '不变' },
      ],
    }
  },
  // camera=摄像头参数
  props: ['camera'],

  created() {
    this.getScreenStatus()
  },
  methods: {
    // 获取屏幕状态
    getScreenStatus() {
      api.then((e) => {
        e.getStatusInfo({ op: 'getRotate' }).then((response) => {
          this.rotateScreen = response.data
          // console.log('屏幕状态',response);
        })
      })
    },
    // 获取摄像头状态
    getCamera() {},
    // 旋转屏幕
    setScreen() {
      var text = {
        plugin: 'Device',
        action: 'DEVICE_RTURN',
        value: this.rotateScreen,
      }
      text2 = {
        MsgType: 'Text',
        Receiver: 'Device',
        Data: text,
      }
      // console.log("text1", text);
      // 第一次发送

      text1 = {
        MsgType: 'LoadPlugin',
        Receiver: 'ControlCenter',
        Data: 'Device',
      }
      // console.log("text2", text);
      // 第二次发送
      ZM.send(text1)
      ZM.send(text2)
    },

    // 旋转摄像头
    setCamera() {
      api.then((e) => {
        e.getConfig({
          op: 'setconfig',
          data: { CAMERA: { enable: true, flip: this.camera.flip } },
        }).then((response) => {
          // console.log("setconfig", response);
          // console.log("camera.flip", this.camera.flip);

          //修改成功发给合成
          text2 = {
            MsgType: 'Text',
            Receiver: 'SpeechSynthesis',
            Data: '保存配置成功，您需要重启后生效！',
          }

          ZM.send(text2)
        })
      })
    },
    // 关闭屏幕
    screenOff() {
      text1 = {
        MsgType: 'Text',
        Receiver: 'ControlCenter',
        Data: '关闭屏幕',
      }
      // console.log("关闭屏幕");
      // 第二次发送

      ZM.send(text1)

      setTimeout(() => {
        this.isOn = true
      }, 3000)
    },
  },
}
</script>

<style scoped>
.switch-button {
  width: 100%;
  height: 100%;
}

.switch-box {
  padding: 0 10px;
}

.switch-button > div:first-child {
  position: relative;
  height: 10%;
  font-size: 13px;
  /* font-weight: 400; */
  background-color: #c4c1c1;
}

.switch-button > div:first-child span {
  position: absolute;
  top: 50%;
  margin-left: 5px;
  transform: translateY(-50%);
  color: rgb(126, 125, 125);
  letter-spacing: 3px;
}

.switch-box {
  height: 90%;
}

.switch-box span {
  font-size: 15px;
}

.rotate-screen {
  height: 40%;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  border-bottom: 1px solid gray;
}

.rotate-screen span {
  padding-left: 9px;
  color: #409eff;
}

.el-select {
  align-self: flex-end;
}

.rotate-camera {
  height: 40%;

  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  border-bottom: 1px solid gray;
}

.rotate-camera span {
  /* width: 30%; */
  padding-left: 9px;
  color: #409eff;
}

.close-screen {
  height: 20%;
  position: relative;
}
.close-screen > div {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.close-screen .el-switch {
  margin-left: 15px;
}

.el-select {
  width: 70%;
}
</style>
