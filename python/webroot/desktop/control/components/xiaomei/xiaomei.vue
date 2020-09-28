<template>
  <div class="xiaomei">
    <!-- <div class="el-icon-microphone">小美</div> -->
    <div v-show="isShow" class="bgc-img" @click="clickXiaomei"></div>

    <el-drawer
      title="我是标题"
      :visible.sync="drawer"
      :direction="direction"
      :before-close="handleClose"
      :with-header="false"
    >
      <span>你好,请说</span>
    </el-drawer>
  </div>
</template>

<script>
module.exports = {
  data() {
    return {
      isShow: true,

      drawer: false,
      direction: "btt"
    };
  },
  methods: {
    clickXiaomei() {
      this.isShow = false;
      this.drawer = true;
      console.log("test");
    },

    handleClose(done) {
      setTimeout(() => {
        this.isShow = true;
      }, 300);
      this.drawer = false;
    }
  }
};
</script>

<style scoped>
/* .el-icon-microphone {
  width: 130px;
  height: 80px;
  background-color: aqua;
  font-size: 40px;
  line-height: 80px;
} */

.xiaomei {
  width: 100px;
  height: 100px;
  /* background-color: pink; */
}

.bgc-img {
  width: 100%;
  height: 100%;
  /* background-color: purple; */
  background-image: url(./img/xiaomei.png);
  background-position: center;
  background-size: 80%;
  background-repeat: no-repeat;
  border-radius: 10px;

  transition: 0.4s;
}

.bgc-img:hover {
  background-size: 100%;
}
</style>
