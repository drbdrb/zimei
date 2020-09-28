<template>
  <div class="app-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <el-progress type="dashboard" :percentage="cpuuse" :color="colors"></el-progress>
          <div>CPU使用率</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <el-progress type="dashboard" :percentage="cputemp" :color="colors"></el-progress>
          <div>CPU温度</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <el-progress type="dashboard" :percentage="ramuse" :color="colors"></el-progress>
          <div>内存使用率</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="grid-content bg-purple">
          <el-progress type="dashboard" :percentage="diskues" :color="colors"></el-progress>
          <div>磁盘使用率</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
var api = import("/admin/api/index.js");

module.exports = {
  data() {
    return {
      timer: "",
      cputemp: 0,
      cpuuse: 0,
      ramuse: 0,
      diskues: 0,
      percentage: 15,
      colors: [
        { color: "#f56c6c", percentage: 20 },
        { color: "#e6a23c", percentage: 40 },
        { color: "#5cb87a", percentage: 60 },
        { color: "#1989fa", percentage: 80 },
        { color: "#6f7ad3", percentage: 100 }
      ]
    };
  },
  // 页面载入后触发
  created() {
    this.fetchData();
  },
  methods: {
    getdata() {
      api.then(e => {
        e.getStatusInfo({ op: "getallinfo" }).then(response => {
          const data = response.data;
          this.cputemp = parseInt(data.cpuTemp);
          this.cpuuse = parseInt(data.cpuUse);
          this.ramuse = parseInt(data.ramUse);
          this.diskues = parseInt(data.diskUes);
        });
      });
    },
    fetchData() {
      this.listLoading = true;
      this.getdata();
      this.listLoading = false;
    }
  },
  mounted() {
    this.timer = setInterval(this.getdata, 1000);
  },
  beforeDestroy() {
    clearInterval(this.timer);
  }
};
</script>

<style>
.grid-content {
  text-align: center;
}
</style>
