<template>
  <div>
    <h3>{{msg}}</h3>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      msg: "加载组件成功"
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.msg = this.msg + "-中文";
    }
  }
};
</script>

<style scoped>
</style>
