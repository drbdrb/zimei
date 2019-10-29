import wificore as wificore
import json

def application(env, start_response, response_state):
    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    start_response(status, headers)

    if type(env['DATA']) is dict:
        set_json = env['DATA']

        wifico = wificore.Wificore()
        #初始化网络状态
        wifico.config_wifi(set_json)

        ret_str = {"code":"0000","msg":"正在验证网络"}
    else:
        ret_str = {"code":"9999","msg":"数据格式错误"}

    response_state( env )

    return json.dumps( ret_str )