<template>
  <div class="app-container">
    <el-tabs v-model="activeName">
      <el-tab-pane label="基本配置" name="base_tabs">
        <el-form ref="form" v-loading="listLoading" :model="config_base" label-width="120px">
          <el-form-item label="插件名">
            <el-input v-model="config_base.name" :disabled="true" />
          </el-form-item>
          <el-form-item label="中文简称">
            <el-input v-model="config_base.displayName" />
          </el-form-item>
          <el-form-item label="简介">
            <el-input v-model="config_base.description" type="textarea" />
          </el-form-item>
          <el-form-item label="语音触发词">
            <el-tag
              v-for="tag in config_base.triggerwords"
              :key="tag"
              closable
              :disable-transitions="false"
              @close="handleClose(tag)"
            >{{ tag }}</el-tag>
            <template v-if="inputVisible">
            <el-input
              ref="saveTagInput"
              v-model="inputValue"
              class="input-new-tag"
              size="small"
              @keyup.enter.native="handleInputConfirm"
              @blur="handleInputConfirm"
            />
            </template>
            <template v-else>
              <el-button class="button-new-tag" size="small" @click="showInput">+ 添加触发词</el-button>
            </template>
          </el-form-item>
          <el-form-item label="系统插件">
            <el-switch v-model="config_base.IsSystem" />
            <span class="tishi">系统插件：是指被触发启动后会一直保持在后台运行</span>
          </el-form-item>
          <el-form-item label="自动启动">
            <el-switch v-model="config_base.AutoLoader" />
            <span class="tishi">自动启动：是指此插件会随系统同时启动并保持在后台运行</span>
          </el-form-item>
          <el-form-item label="插件状态：">
            <el-switch v-model="config_base.IsEnable" />
          </el-form-item>
          <el-form-item>
            <el-button type="success" @click="onSavebase"> 保 存 </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="版本维护" name="update_tabs">
        <el-form ref="mainten" label-width="120px" :model="mainten">
          <el-form-item label="当前版本：">
            V{{ mainten.version }}版
            <el-button type="warning" size="mini" :disabled="check_butt.disabled" :loading="check_butt.loading" @click="onCheckVer">{{ check_butt.butttext }}</el-button>
            <div v-if="check_butt.tishi">
              {{ check_butt.msg }}
              <el-button v-if="check_butt.isupgrade==1" type="success" size="mini" :disabled="update_butt.disabled" :loading="check_butt.loading" @click="onUpdate">{{ update_butt.butttext }}</el-button>
            </div>
          </el-form-item>
          <el-form-item label="插件管理：">
            <el-button type="danger" size="mini" :disabled="unistall_butt.disabled" @click="onRemove">{{ unistall_butt.butttext }}</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane v-if="release.isRelease==0" label="发布插件" name="release_tabs">
        <el-form ref="release" label-width="120px" :model="release">
          <el-form-item label="版本维护URL" prop="repository_url" :rules="[{ required: true, message: '版本维护URL：不能为空'}]">
            <el-input v-model="release.repository_url" size="small" style="width:500px;" />
          </el-form-item>
          <el-form-item label="插件开发者：" prop="author" :rules="[{ required: true, message: '插件开发者：不能为空'}]">
            <span>{{ release.author }}</span>
            <el-button v-if="develop.showloginbutt" type="primary" plain size="mini" @click="onShowLogin">登录发布者账号</el-button>
          </el-form-item>
          <el-form-item label="">
            <el-button type="success" size="small" :disabled="release_butt.disabled" @click="onRelease('release')">发布插件</el-button>
          </el-form-item>
        </el-form>
        <el-dialog :key="develop.openkey" title="登录开发者账号" :visible.sync="develop.showlogin" width="400px" center @close="closeDialog">
          <el-form ref="develop" label-width="88px" :model="develop" :rules="rules">
            <el-form-item label="账 号:" prop="username">
              <el-input v-model="develop.username" autocomplete="off" size="small" placeholder="请输入账号/Email格式" />
            </el-form-item>
            <el-form-item label="密 码:" prop="userpass">
              <el-input v-model="develop.userpass" autocomplete="off" size="small" show-password placeholder="请输入密码" />
            </el-form-item>
            <el-form-item v-if="develop_butt.loginbutt=='立即注册'" label="确认密码:" prop="confpass">
              <el-input v-model="develop.confpass" autocomplete="off" size="small" show-password placeholder="请再输入一次密码" />
            </el-form-item>
            <el-form-item center>
              <el-button :type="develop_butt.type" @click="onLoginUser('develop')">{{ develop_butt.loginbutt }}</el-button>
              <el-button type="text" @click="onStartReg">{{ develop_butt.reginbutt }}</el-button>
            </el-form-item>
          </el-form>
          <el-form ref="dev_wxchat" label-width="88px">
            <el-form-item label="第三方登录:">
              <span class="iconfont icon-weixin"></span> <el-button type="text" @click="wxchatLogin">微信登录</el-button>
            </el-form-item>
          </el-form>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
var openwindow = import('/admin/utils/open-window.js').then((e) => { return e.default });
var api = import('/admin/api/plugin.js');
var user = import('/admin/api/user.js');

module.exports = {
  data() {
    // ================== 验证开发者登录表单 =======================
    var validateName = (rule, value, callback) => {
      const mailReg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/
      if (!value) {
        return callback(new Error('登录账号不能为空'))
      }
      setTimeout(() => {
        if (mailReg.test(value)) {
          callback()
        } else {
          callback(new Error('请输入正确开发者账号，格式为：Email'))
        }
      }, 100)
    }

    var validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (this.develop.confpass !== '') {
          this.$refs.develop.validateField('confpass')
        }
        callback()
      }
    }

    var validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.develop.userpass) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    // ================= 验证开发者登录表单 End =======================

    return {
      // tabs 选项
      activeName: 'base_tabs',

      // 插件信息
      config_base: {},

      // 版本维护
      mainten: {},

      // 发布管理
      release: {},

      // 插件控制信息
      form_control: [],

      // 开发者信息
      develop: {
        showloginbutt: true,
        showlogin: false,
        username: '',
        userpass: ''
      },

      default_val: {
        slider: 20
      },

      inputVisible: false,
      inputValue: '',
      listLoading: true,

      // 远程更新类型
      repository_opint: [
        {
          value: 'git',
          label: 'GIT'
        }, {
          value: 'http',
          label: 'HTTP'
        }
      ],

      // 检查更新提示
      check_butt: {
        loading: false,
        butttext: '检查更新',
        disabled: false,
        tishi: false,
        msg: '',
        isupgrade: 0
      },

      // 检查更新按钮定义
      update_butt: {
        butttext: '立即升级',
        disabled: false,
        loading: false
      },

      // 卸载按钮定义
      unistall_butt: {
        disabled: false,
        butttext: '卸载插件'
      },

      // 发布按钮定义
      release_butt: {
        disabled: false,
        butttext: '发布插件'
      },

      // 开发者登录按钮
      develop_butt: {
        type: 'success',
        loginbutt: '立即登录',
        reginbutt: '注册'
      },

      // 开发者登录表单验证
      rules: {
        username: [
          { validator: validateName, trigger: 'blur' }
        ],
        userpass: [
          { validator: validatePass, trigger: 'blur' }
        ],
        confpass: [
          { validator: validatePass2, trigger: 'blur' }
        ]
      },

      input3: ''
    }
  },

  // 页面载入后触发
  created() {
    this.fetchData()
    window.addEventListener('hashchange', this.afterQRScan)
  },

  methods: {
    // 加载基本数据
    fetchData() {
      this.listLoading = true
      var pluginName = this.$route.query.name
      api.then((e) => {
        e.getList({ op: 'getinfo', name: pluginName }).then(response => {
          const data = response.data
          // 基本设置
          this.config_base = {
            name: data.name,
            displayName: data.displayName,
            description: data.description,
            triggerwords: data.triggerwords,
            IsSystem: data.IsSystem,
            AutoLoader: data.AutoLoader,
            IsEnable: data.IsEnable
          }
          // 移动端控制
          this.form_control = data.control

          // 版本维护
          this.mainten = {
            version: data.version
          }

          this.release = {
            repository_type: data.repository.type,
            repository_url: data.repository.url,
            isRelease: data.isRelease,
            author: ''
          }
          if (data['author']) { this.mainten['author'] = data['author'] }

          this.listLoading = false
        })
      })
    },

    // ------------ 触发词 START ---------------
    handleClose(tag) {
      this.config_base.triggerwords.splice(this.config_base.triggerwords.indexOf(tag), 1)
    },

    showInput() {
      this.inputVisible = true
      this.$nextTick(_ => {
        this.$refs.saveTagInput.$refs.input.focus()
      })
    },
    handleInputConfirm() {
      const inputValue = this.inputValue
      if (inputValue) {
        this.config_base.triggerwords.push(inputValue)
      }
      this.inputVisible = false
      this.inputValue = ''
    },
    // ------------- 触发词 END --------------

    // 保存基本信息
    onSavebase() {
      api.then((e) => {
        e.updateConfig({ op: 'setconfig', data: this.config_base }).then(response => {
          const data = response.data
          if (data.error === '0000') {
            this.$message({
              message: response.message,
              type: 'success'
            })
          } else {
            this.$message.error(response.message)
          }
        })
      })
    },

    goBack() {
      this.$router.replace({
        path: '/chajian/myplugin'
      })
    },

    // ========== 保存基本信息 END ==============

    // 检查更新
    onCheckVer: function() {
      this.check_butt.butttext = '正在检查更新中……'
      this.check_butt.loading = true
      this.check_butt.disabled = true
      this.check_butt.tishi = false
      const pluginName = this.config_base.name
      api.then((e) => {
        e.updatePlugin({ op: 'checkver', name: pluginName }).then(response => {
          this.check_butt.tishi = true
          if (response.code === 20000) {
            var data = response.data
            if (data.error === '0000') {
              const data = response.data
              this.check_butt.isupgrade = data.upgrade
              this.check_butt.msg = response.message + '[ 最新版：' + data.newversion + ' ]'
            } else {
              this.check_butt.msg = response.message
            }
          } else {
            this.check_butt.msg = response.message
          }
          this.check_butt.butttext = '检查更新'
          this.check_butt.loading = false
          this.check_butt.disabled = false
        })
      })
    },

    // 升级插件
    onUpdate: function() {
      this.update_butt.butttext = '正在升级中……'
      this.update_butt.loading = true
      this.update_butt.disabled = true
      this.check_butt.disabled = true
      const pluginName = this.config_base.name
      api.then((e) => {
        e.updatePlugin({ op: 'update', name: pluginName }).then(response => {
          if (response.code === 20000) {
            var data = response.data
            if (data.error === '0000') {
              this.$message({
                message: response.message,
                type: 'success'
              })
              this.mainten.version = data.version
            } else {
              this.$message.error(response.message)
            }
          } else {
            this.$message.error(response.message)
          }
          this.update_butt.butttext = '立即升级'
          this.update_butt.loading = false
          this.update_butt.disabled = false
          this.check_butt.disabled = false
        })
      })
    },

    // 卸载插件
    onRemove: function() {
      this.unistall_butt.disabled = true
      this.$confirm('此操作将永久删除该插件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.unistall_butt.butttext = '正在卸载……'
        const pluginName = this.config_base.name
        api.then((e) => {
          e.updatePlugin({ op: 'uninstall', name: pluginName }).then(response => {
            if (response.code === 20000) {
              var data = response.data
              if (data.error === '0000') {
                this.$message({
                  message: response.message,
                  type: 'success'
                })
                this.$router.replace({
                  path: '/chajian/myplugin'
                })
                return true;
              } else {
                this.$message.error(response.message)
                this.unistall_butt.butttext = '卸载插件'
                this.unistall_butt.disabled = false
              }
            } else {
              this.$message.error(response.message)
              this.unistall_butt.butttext = '卸载插件'
              this.unistall_butt.disabled = false
            }
          })
        })
      }).catch(() => {
        this.unistall_butt.disabled = false
      })
    },

    // ====================== 开发者账号 Start ==============================
    // 登录开发者账号
    onShowLogin: function() {
      this.develop.showfindpass = false
      this.develop.openkey = 'k_' + Math.random().toString()
      this.develop_butt.loginbutt = '立即注册'
      this.onStartReg()
      this.develop.showlogin = true
    },

    // 关闭登录框
    closeDialog: function() {
      localStorage.removeItem('x-admin-oauth-code')
    },

    // 登录开发者账号
    onLoginUser: function(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          var op = ''
          if (this.develop_butt.loginbutt === '立即登录') {
            op = 'login'
          } else {
            op = 'regist'
          }
          const post_data = {
            op: op,
            username: this.develop.username,
            userpass: this.develop.userpass
          }
          user.then((e) =>{
            e.loginDevelop(post_data).then(response => {
              if (response.code === 20000) {
                const data = response.data
                if (data['error'] === '0000') {
                  this.release.author = data['username']
                  this.release.webuid = data['webuid']
                  this.develop.showlogin = false
                  this.$message({ message: response.message, type: 'success' })
                } else {
                  this.release.author = ''
                  this.release.webuid = ''
                  this.$message.error(response.message)
                }
              }
            })
          })
        } else {
          return false
        }
      })
    },

    // 打开注册开发者账号
    onStartReg: function() {
      if (this.develop_butt.loginbutt === '立即登录') {
        this.develop_butt.type = 'primary'
        this.develop_butt.loginbutt = '立即注册'
        this.develop_butt.reginbutt = '已有账号，马上登录'
      } else {
        this.develop_butt.type = 'success'
        this.develop_butt.loginbutt = '立即登录'
        this.develop_butt.reginbutt = '没有账号，立即注册'
      }
    },

    // 微信登录
    wxchatLogin: function() {
      var host = window.location.host +'@admin@pages@login@authredirect.html'
      host = host.replace(/@@/g, '@')
      var _this = this
      openwindow.then((e) => {e('http://hapi.16302.com/login/wxlogin/host/' + host, '微信登录', 500, 500)});
      window.localStorage.setItem('x-admin-oauth-code', '')
      var logtimer = setInterval(function() {
        var oauthcode = localStorage.getItem('x-admin-oauth-code')
        if (oauthcode == null) {
          clearInterval(logtimer)
          return false
        }
        if (oauthcode) {
          var theRequest = {}
          var strs = oauthcode.split('&')
          for (let i = 0; i < strs.length; i++) {
            var item = strs[i].split('=')
            theRequest[item[0]] = decodeURI(item[1])
          }
          if (theRequest['state'] && theRequest['state'] === 'yes') {
            _this.release.author = theRequest['nickname']
            _this.release.webuid = theRequest['webuid']
            _this.develop.showlogin = false
            _this.develop.showloginbutt = false
          } else {
            this.$message.error('登录开发者账号失败，请重新登录试试。')
          }
        }
      }, 500)
    },

    // ====================== 开发者账号 End ==============================

    // 发布插件
    onRelease: function(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          var post_data = {
            op: 'release',
            name: this.config_base.name,
            author: this.release.author,
            webuid: this.release.webuid
          }
          api.then((e)=>{
            e.updatePlugin(post_data).then(response => {
              if (response.code === 20000) {
                var data = response.data
                if (data.error === 0) {
                  this.$alert(response.message, '恭喜您，插件发布成功！')
                  return true
                } else {
                  this.$message.error(response.message)
                  return false
                }
              }
            })
          })
        } else {
          return false
        }
      })
    },
    // ======= 触发词 END =========
    log: function(evt) {
      window.console.log(evt)
    }
  }
}
</script>

<style>
  .mobile {
    border:2px solid #CCC;
    border-radius: 3px;
    width: 350px;
    height: 550px;
    margin: 10px auto;
    padding: 5px;
  }

  .list-group{
    border:1px solid #CCC;
    padding: 2px;
    min-height:30px;
    margin: 0 0 8px 0;
  }

  .tishi{
    padding-left:10px
  }
  .el-tag + .el-tag {
    margin-left: 10px;
  }
  .button-new-tag {
    margin-left: 10px;
    height: 32px;
    line-height: 30px;
    padding-top: 0;
    padding-bottom: 0;
  }
  .input-new-tag {
    width: 90px;
    margin-left: 10px;
    vertical-align: bottom;
  }
  .el-button+.el-button{
    margin:2px 5px
  }
  .my-lable{
    font-size: 14px;
    border-bottom: 1px solid #cccccc;
    padding: 5px 0 5px 5px;
    margin:0 0 5px 0px
  }

  .add-lable{
    border:1px solid #CCC;
    border-radius: 3px;
    width: 350px;
    height: 140px;
    margin: 10px auto;
    padding: 5px;
  }
  .al-title{
    line-height: 28px;
    text-align: center;
    font-weight: bold;
    font-size: 16px;
  }
  .el-form-item {
    margin-bottom: 12px;
  }
  .add-button{
    border:1px solid #CCC;
    border-radius: 3px;
    width: 350px;
    height: auto;
    min-height: 300px;
    margin: 10px auto;
    padding: 5px;
  }
  .titlered .el-dialog__title{color: #FF0000;font-weight: bold;}
</style>
