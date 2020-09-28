<template>
  <div>
    <i class="el-icon-message-solid">:{{volume}}</i>
  </div>
</template>

<script>
module.exports = {
  props: ["volume"]
};
</script>

<style scoped>
i {
  margin-left: 5px;
  line-height: 50px;
  font-size: 25px;
  height: 50px;
  color: #fff;
}
</style>
