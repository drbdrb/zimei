<template>
  <div class="systemtitle">
    <!-- <span class="title">{{msg}}</span> -->
    <span class="title">{{sysTitle}}</span>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      msg: "caonima"
    };
  },
  props: ["sysTitle"]
};
</script>

<style scoped>
.systemtitle {
  width: 100%;
  height: 100%;
}

.title {
  color: #fff;
  font-size: 25px;
  margin-left: 10px;
}
</style>
