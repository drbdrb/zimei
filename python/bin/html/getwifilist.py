import time,os,re,json
import math

def takeSecond(elem):
    return int(elem['wifi_qual'])


def application(env, start_response, response_state ):

    status = "200 OK"
    headers = [("Content-Type", "text/plain")]

    start_response(status, headers)

    iwlist = 'sudo iwlist wlan0 scan | grep -E "ESSID|Quality|IEEE"'
    cmd_str = os.popen(iwlist).read()
    cmd_str = cmd_str.strip()
    cmd_str = re.sub(r'\\x00','',cmd_str)

    res = cmd_str.split("Quality")

    re_name = r'ESSID:"(.+)"'
    re_pass = r'IE:\s+IEEE\s+(.+)\s+Version'
    re_qual = r'\=(\d+)\/(\d+)'

    wifi_list = []
    for x in res:
        item_obj = {}
        o_n = re.search( re_name, x, re.M|re.I)
        if o_n:
            wifi_name = o_n.group(1)
            rem = re.search(r'\\x', wifi_name, re.M|re.I)
            if rem != None:
                wifi_name = wifi_name.encode('raw_unicode_escape').decode()

            if wifi_name:
                item_obj['wifi_name'] = wifi_name
            else:
                continue
        else:
            continue

        o_p = re.search( re_pass, x, re.M|re.I)
        if o_p:
            #print('pass:', o_p.group(1))
            item_obj['wifi_pass'] = o_p.group(1)

        o_l = re.search( re_qual, x, re.M|re.I)
        if o_l:
            #print('pass:', o_l.group(1))
            item_obj['wifi_qual'] = math.floor( (int(o_l.group(1)) / int(o_l.group(2)))*100 )
        if len(item_obj)>0:
            wifi_list.append( item_obj )

    wifi_list.sort(key=takeSecond,reverse=True)

    return json.dumps( wifi_list )