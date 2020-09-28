<template>
  <div>
    <el-row class="plugin-list">
      <el-col :span="6" class="plugin-item">
        <!-- <div class="plugin-box">插件1</div> -->
      </el-col>
    </el-row>
  </div>
</template>

<script>
module.exports = {}
</script>

<style scoped>
.plugin-item {
  height: 20vw;
  padding: 10px;
  border-radius: 5px;
  margin-top: 20px;
}

.plugin-box {
  width: 100%;
  height: 100%;
  /* box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.3); */
  border: 2px solid rgb(177, 173, 173);
}
</style>
