<template>
  <div class="app-container">
    <el-table
      v-loading="listLoading"
      :element-loading-text="loadingText"
      :data="list"
      border
      fit
      highlight-current-row
    >
      <el-table-column label="插件名" width="150">
        <template slot-scope="scope">{{ scope.row.name }}</template>
      </el-table-column>
      <el-table-column label="中文名称" width="180" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.displayname }}</span>
        </template>
      </el-table-column>
      <el-table-column label="简介" align="left">
        <template slot-scope="scope">{{ scope.row.description }}</template>
      </el-table-column>
      <el-table-column class-name="status-col" label="开发者" width="110" align="center">
        <template slot-scope="scope">{{ scope.row.author }}</template>
      </el-table-column>
      <el-table-column label="版本" align="center" width="120">
        <template slot-scope="scope">{{ scope.row.version }}</template>
      </el-table-column>
      <el-table-column label="插件类型" align="center" width="120">
        <template slot-scope="scope">{{ scope.row.type | pluginType }}</template>
      </el-table-column>
      <el-table-column label="安装&升级" align="center" width="120">
        <template slot-scope="scope">
          <el-button :type="scope.row.state | statusFilter" :loading="butt_loading[scope.row.name]" :disabled="butt_disabled[scope.row.name]" size="mini" @click.stop="doAdmin(scope.row.name,scope.row.state)">{{ scope.row.state }}</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>

var api = import('/admin/api/plugin.js');

module.exports = {
  filters: {
    statusFilter(status) {
      const statusMap = {
        '一键安装': 'success',
        '一键升级': 'warning',
        '已安装': ''
      }
      return statusMap[status]
    },
    pluginType(status) {
      const typeMap = {
        0: '第三方插件',
        1: '官方插件',
        2: '认证插件'
      }
      return typeMap[status]
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      loadingText: '数据加载中',
      butt_loading: [],
      butt_disabled: []
    }
  },

  // 页面载入后
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.listLoading = true
      api.then((e) => {
        e.getList({ op: 'getalllist' }).then(response => {
            this.list = response.data
            this.listLoading = false
        })
      })
    },

    // 升级安装操作
    doAdmin(pluginName, state) {
      if (state === '已安装') {
        this.$router.replace({
          path: '/chajian/mypluginedit',
          query: {
            name: pluginName
          }
        })
        return true
      }
      this.butt_loading[pluginName] = true
      this.butt_disabled[pluginName] = true
      this.listLoading = true
      this.loadingText = '正在' + state + pluginName + '插件，请稍候……'
      var op = ''
      if (state === '一键安装') {
        op = 'install'
      } else if (state === '一键升级') {
        op = 'update'
      }
      api.then((e) => {
        e.updatePlugin({ op: op, name: pluginName }).then(response => {
          var data = response.data
          if (state === '一键安装') {
            if (response.code === 20000) {
              if (data.error === '0000') {
                this.fetchData()
                this.$message({
                  message: response.message,
                  type: 'success'
                })
              } else {
                this.$message.error(response.message)
              }
            } else {
              this.$message.error(response.message)
            }
            this.butt_loading[pluginName] = false
            this.butt_disabled[pluginName] = false
            this.listLoading = false
          }
          if (state === '一键升级') {
            if (response.code === 20000) {
              if (data.error === '0000') {
                this.fetchData()
                this.$message({
                  message: response.message,
                  type: 'success'
                })
              } else {
                this.$message.error(response.message)
              }
            } else {
              this.$message.error(response.message)
            }
            this.butt_loading[pluginName] = false
            this.butt_disabled[pluginName] = false
            this.listLoading = false
          }
        })
      })
    }
  }
}
</script>
