var request = import("../utils/request.js").then((e) => {
    return e.default.request;
});

/**
 * 获取设备状态信息
 * @param 请求信息
 */
export function getStatusInfo(params) {
    return request.then((e) => {
        return e({
            url: "/api/admin_index.py",
            method: "get",
            params,
        });
    });
}

/**
 * 更新插件配置信息
 * @param {op: setconfig } 更新插件配置信息
 */
export function updateConfig(params) {
    return request.then((e) => {
        return e({
            url: "/api/plugin_list.py",
            method: "post",
            params,
        });
    });
}

// 插件管理
export function updatePlugin(params) {
    return request.then((e) => {
        return e({
            url: "/api/plugin_update.py",
            method: "get",
            params,
        });
    });
}

// 获取插件列表
export function getPlugins(params) {
    return request.then((e) => {
        return e({
            url: "/api/plugin_list.py",
            method: "get",
            params,
        });
    });
}

// 获取天气信息
export function getWeather(params) {
    return request.then((e) => {
        return e({
            url: "/api/mojing.py",
            method: "get",
            params,
        });
    });
}

// 获取配置信息
export function getConfig(params) {
    return request.then((e) => {
        return e({
            url: "/api/set_config.py",
            method: "get",
            params,
        });
    });
}


