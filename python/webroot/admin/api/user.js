const request =
    import ('../utils/request.js').then((e) => { return e.default.request });

// 后台用户登录
export function login(data) {
    return request.then((e) => {
        return e({
            url: '/api/user_login.py',
            method: 'post',
            data
        })
    })
}

// 获取用户信息
export function getInfo(token) {
    return request.then((e) => {
        return e({
            url: '/api/user_login.py',
            method: 'get',
            params: { token }
        })
    })
}

// 退出登录
export function logout() {
    return request.then((e) => {
        return e({
            url: '/api/user_login.py',
            method: 'post',
            params: { op: 'logout' }
        })
    })
}

// ===================================================

// 登录开发者账号
export function loginDevelop(params) {
    return request.then((e) => {
        return e({
            url: '/api/develop_user.py',
            method: 'post',
            params
        })
    })
}