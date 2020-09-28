<template>
  <div class="app-container">
    <el-form ref="form" v-loading="listLoading" label-width="120px">
      <el-form-item label="当前版本">
        <span>{{ version }}</span>
        <el-button type="primary" size="mini" :loading="check_loading" :disabled="check_disabled" @click="isupdate">检查更新</el-button>
        <span :class="{ yes_upgrade: is_updata, no_upgrade: !is_updata }">{{ check_tishi }}</span>
      </el-form-item>
      <el-form-item label="">
        <el-button v-if="is_updata" type="success" :loading="update_loading" :disabled="update_disabled" @click="startupdate">{{ update_butttext }}</el-button>
      </el-form-item>
      <el-form-item label="">
        <el-progress v-if="is_percent" :percentage="update_progress" status="success" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
var api = import('/admin/api/setconfig.js')

module.exports = {
  data() {
    return {
      version: '0.0.1',
      is_updata: false,
      is_percent: false,
      check_loading: false,
      check_disabled: false,
      update_loading: false,
      update_disabled: false,
      update_progress: 0,
      update_butttext: '开始升级',
      check_tishi: ''
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    // 获取远程版本号判断是否可以升级
    get_remotever() {
      var _this = this
      api.then((e) => {
          e.updateSystem({ op: 'remotever' }).then(response => {
            const data = response.data
            if (data.error !== '0000') {
              setTimeout(() => {
                _this.get_remotever()
              }, 1000)
            } else {
              this.check_loading = false
              this.check_disabled = false
              if (data.upgrade > 0) {
                this.is_updata = true
              } else {
                this.is_updata = false
              }
              this.check_tishi = response.message
            }
          })
    })
    },
    // 获取更新状态
    get_progress() {
      var _this = this
      api.then((e) => {
        e.updateSystem({ op: 'updatestate' }).then(response => {
          const data = response.data
          if (data.error !== '0000') {
            setTimeout(() => {
              _this.get_progress()
            }, 1000)
          } else {
            var progress = parseInt(data.progress)
            if (this.update_progress >= 0 && this.update_progress < 90) {
              this.update_progress = this.update_progress + 1
            }
            if (progress > 0 && progress > this.update_progress) {
              this.update_progress = progress
            }
            if (progress < 100) {
              setTimeout(() => {
                _this.get_progress()
              }, 1000)
            } else {
              this.$alert('恭喜您，系统升级成功！', '自美系统', {
                confirmButtonText: '确定',
                callback: action => {
                  this.$router.replace({path:'/index/index'})
                }
              })
              return
            }
          }
        })
      })
    },
    // 获取本地版本号
    fetchData() {
      this.listLoading = true
      api.then((e) => {
        e.updateSystem({ op: 'localver' }).then(response => {
          const data = response.data
          this.version = data.version
          this.listLoading = false
        })
      })
    },
    // 提交升级请求，判断是否可升级
    isupdate() {
      this.check_loading = true
      this.check_disabled = true
      this.is_updata = false
      api.then((e)=> {
        e.updateSystem({ op: 'isupdate' }).then(response => {
          const data = response.data
          if (data.error === '0000') {
            this.check_tishi = '正在获取远程最新版本，请稍候……'
            setTimeout(() => {
              this.get_remotever()
            }, 1000)
          }
        })
      })
    },
    // 开始升级
    startupdate() {
      this.update_loading = true
      this.check_disabled = true
      this.update_disabled = true
      this.update_butttext = "正在升级……，请稍候！（不要离开此页面，待升级工作完成系统会自动重启设备）"
      this.is_percent = true
      api.then((e) => {
        e.updateSystem({ op: 'startupdate' }).then(response => {
          const data = response.data
          if (data.error === '0000') {
            this.get_progress()
          }
        })
      })
    }
  }
}
</script>

<style scoped>
.line {text-align: center;}
.yes_upgrade{color: crimson;}
.no_upgrade{color: rgb(33, 163, 0);}
</style>

