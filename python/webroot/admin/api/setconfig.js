const request =
    import ('../utils/request.js').then((e) => { return e.default.request });

export function getConfig(params) {
    return request.then((e) => {
        return e({
            url: '/api/set_config.py',
            method: 'get',
            params
        })
    })
}

export function setConfig(params) {
    return request.then((e) => {
        return e({
            url: '/api/set_config.py',
            method: 'post',
            params
        })
    })
}

// 更新系统
export function updateSystem(params) {
    return request.then((e) => {
        return e({
            url: '/api/system_update.py',
            method: 'get',
            params
        })
    })
}