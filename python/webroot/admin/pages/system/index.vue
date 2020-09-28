<template>
  <div class="app-container">
    <el-form ref="form" v-loading="listLoading" label-width="200px">
      <el-form-item v-for="(item, index) in setconfig" :key="index" :label="item.note">
        <el-form v-if="item.more" label-width="200px">
          <el-form-item v-for="(moitem, moindex) in item.more" :key="moindex" :label="moitem.note">
            <el-radio-group v-if="moitem.radio" v-model="config[index][moindex]" size="mini">
              <el-radio-button
                v-for="(ikey, iind) in moitem.radio"
                :key="iind"
                :label="iind"
              >{{ ikey }}</el-radio-button>
            </el-radio-group>

            <el-select v-if="moitem.select" v-model="config[index][moindex]" placeholder="请选择" size="mini">
              <el-option
                v-for="(ikey, iind) in moitem.select"
                :key="iind"
                :label="ikey"
                :value="iind"
              />
            </el-select>
            <el-switch
              v-if="moitem.switch"
              v-model="config[index][moindex]"
              active-color="#13ce66"
              inactive-color="#ff4949"
            />
          </el-form-item>
        </el-form>
        <el-select v-if="item.select" v-model="config[index]" placeholder="请选择">
          <el-option
            v-for="(ikey, iind) in item.select"
            :key="iind"
            :label="ikey"
            :value="iind"
          />
        </el-select>
        <el-switch
          v-if="item.switch"
          v-model="config[index]"
          active-color="#13ce66"
          inactive-color="#ff4949"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="success" @click="submitForm"> 保 存 </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
var api = import('/admin/api/setconfig.js');

module.exports = {
  data() {
    return {
      config: [],
      setconfig: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      api.then((e)=> {
        e.getConfig({ op: 'getconfig' }).then(response => {
          const data = response.data
          this.config = data.config
          this.setconfig = data.setconfig
          this.listLoading = false
        })
      })
    },
    submitForm() {
      var post_config = {}
      for (const key in this.setconfig) {
        if (this.setconfig.hasOwnProperty(key)) {
          post_config[key] = this.config[key]
        }
      }
      var post_json_str = JSON.stringify(post_config)
      var post_data = {
        op: 'setconfig',
        data: post_json_str
      }
      api.then((e) => {
        e.setConfig(post_data).then(response => {
          var data = response.data
          if (data.error === '0000') {
            this.$message({
              message: response.message,
              type: 'success'
            })
          }
        })
      })
    }
  }
}
</script>

<style scoped>
.line {
  text-align: center;
}
</style>

