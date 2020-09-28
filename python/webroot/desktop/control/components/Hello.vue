<template>
  <div>
    <h3>http-vue-loader加载成功</h3>
    <el-button type="primary" @click="routelink()">跳转</el-button>
  </div>
</template>

<script>
module.exports = {
  methods: {
    routelink() {
      this.$router.replace({
        path: "example",
        query: {}
      });
    }
  }
};
</script>

 
<style>
</style>