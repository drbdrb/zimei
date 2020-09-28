var request =
    import ('../utils/request.js').then((e) => { return e.default.request });

/**
 * 获取插件列表信息
 * 单个插件信息
 * @param 请求信息
 */
export function getList(params) {
    return request.then((e) => {
        return e({
            url: '/api/plugin_list.py',
            method: 'get',
            params
        })
    })
}

/**
 * 更新插件配置信息
 * @param {op: setconfig } 更新插件配置信息
 */
export function updateConfig(params) {
    return request.then((e) => {
        return e({
            url: '/api/plugin_list.py',
            method: 'post',
            params
        })
    })
}

// 插件管理
export function updatePlugin(params) {
    return request.then((e) => {
        return e({
            url: '/api/plugin_update.py',
            method: 'get',
            params
        });
    })
}