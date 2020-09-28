<template>
  <div class="app-container">
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row
    >
      <el-table-column label="插件名" width="120">
        <template slot-scope="scope">{{ scope.row.name }}</template>
      </el-table-column>
      <el-table-column label="中文名称" width="140">
        <template slot-scope="scope">
          <span>{{ scope.row.displayName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="触发词" align="left">
        <template slot-scope="scope">
          <el-tag
            v-for="tag in scope.row.triggerwords"
            :key="tag"
            type="info"
            size="mini"
          >{{ tag }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="状态" width="100" align="center">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.IsEnable===true" type="success">启用</el-tag>
          <el-tag v-else type="info">禁用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="版本" align="center" width="100">
        <template slot-scope="scope">ν{{ scope.row.version }}</template>
      </el-table-column>
      <el-table-column label="管理" align="center" width="100">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="doAdmin(scope.row.name)">管理</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
var api = import('/admin/api/plugin.js');

module.exports = {
  data() {
    return {
      list: null,
      listLoading: true
    }
  },
  // 页面载入后
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
        this.listLoading = true;
        api.then((e) => {
            e.getList({ op: 'getlist' }).then(response => {
                this.list = response.data
                this.listLoading = false
            })
        })
    },
    doAdmin(pluginNmae) {
      this.$router.replace({
          path: '/chajian/mypluginedit',
          query: {
            name: pluginNmae
          }
      })
    }
  }
}
</script>
<style>
.el-table td, .el-table th{
  padding: 5px 3px;
}
.el-tag {
  margin: 0 1px 0 0;
}
</style>
