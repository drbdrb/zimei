<template>
  <div class="hardware">
    <div class="title">
      <span>硬件信息</span>
    </div>

    <div class="containaer">
      <div>
        <!-- cpu使用率 -->
        <span class="hard-info">cpu使用率</span>
        <el-progress
          :stroke-width="10"
          :show-text="false"
          :color="colors"
          :percentage="hardWareInfo.cpuuse"
        ></el-progress>
      </div>
      <div>
        <!-- cpu温度 -->
        <span class="hard-info">cpu温度</span>
        <el-progress
          :stroke-width="10"
          :show-text="false"
          :color="colors"
          :percentage="hardWareInfo.cputemp"
        ></el-progress>
      </div>
      <div>
        <!-- 内存使用率 -->
        <span class="hard-info">内存使用率</span>
        <el-progress
          :stroke-width="10"
          :show-text="false"
          :color="colors"
          :percentage="hardWareInfo.ramuse"
        ></el-progress>
      </div>
      <div>
        <!-- 磁盘使用率 -->
        <span class="hard-info">磁盘使用率</span>
        <el-progress
          :stroke-width="10"
          :show-text="false"
          :color="colors"
          :percentage="hardWareInfo.diskues"
        ></el-progress>
      </div>
    </div>
  </div>
</template>

<script>
var api = import('/desktop/control/api/index.js')
module.exports = {
  data() {
    return {
      diskues: 0,
      percentage: 15,
      colors: [
        { color: '#f56c6c', percentage: 20 },
        { color: '#e6a23c', percentage: 40 },
        { color: '#5cb87a', percentage: 60 },
        { color: '#1989fa', percentage: 80 },
        { color: '#6f7ad3', percentage: 100 },
      ],

      timer: '',

      hardWareInfo: {
        cputemp: 20,
        cpuuse: 30,
        ramuse: 40,
        diskues: 50,
      },
    }
  },

  created() {
    this.getHardwareInfo()
    this.timer = setInterval(this.getHardwareInfo, 5000)
  },

  methods: {
    getHardwareInfo() {
      api.then((e) => {
        e.getStatusInfo({ op: 'getallinfo' }).then((response) => {
          // console.log("硬件信息", response.data);
          const data = response.data
          this.hardWareInfo.cputemp = parseInt(data.cpuTemp)
          this.hardWareInfo.cpuuse = parseInt(data.cpuUse)
          this.hardWareInfo.ramuse = parseInt(data.ramUse)
          this.hardWareInfo.diskues = parseInt(data.diskUes)
        })
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
.hardware {
  width: 100%;
  height: 100%;
  /* background-color: pink; */
}

.title {
  position: relative;
  height: 10%;
  font-size: 13px;
  background-color: #c4c1c1;
  letter-spacing: 3px;
}

.title span {
  position: absolute;
  top: 50%;
  margin-left: 5px;
  transform: translateY(-50%);
  color: rgb(126, 125, 125);
}

.containaer {
  height: 90%;

  /* background-color: plum; */
}

.containaer > div {
  padding: 0 10px;
  height: 25%;
  /* background-color: yellowgreen; */
  /* border-bottom: 1px solid #000; */
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;

  font-size: 14px;
}
</style>