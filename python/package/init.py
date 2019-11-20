import os
import sqlite3

class systeminit():

    def __init__(self, this_path):
        self.ver_file   = os.path.join(this_path, 'python/data/ver.txt')
        self.config_py  = os.path.join(this_path, 'python/data/config.py')
        self.database   = os.path.join(this_path, 'python/data/config.db')
        self.connection = sqlite3.connect(self.database)

    def search_list(self,lists,key):
        for item in lists:
            if item[0]==key:
                return item
        return False

    def main(self):
        cursor = self.connection.cursor()
        cursor.execute("select * from config order by id")
        rs = cursor.fetchall()
        cursor.close()
        self.connection.close()

        conf_tab = {}
        key_i = 0
        for item in rs:
            if int(item[3])==0:
                if item[0] not in conf_tab:
                    conf_tab[item[0]] = {'key':item[1],'val':item[2]}
            else:
                if item[3] in conf_tab:
                    if type(conf_tab[ item[3] ]['val']) is not dict:
                        conf_tab[ item[3] ]['val'] = {item[1]:item[2]}
                    else:
                        conf_tab[ item[3] ]['val'].setdefault(item[1],item[2])
                else:
                    p_item = self.search_list(rs,item[3])
                    if len(p_item)>0:
                        conf_tab[p_item[0]] = {'key': p_item[1],'val': {item[1]:item[2]} }
            if item[0] > key_i:
                key_i = item[0]

        f = open(self.ver_file,"r")
        fstr = f.read()
        f.close()
        if len(fstr)>0:
            key_i += 1
            conf_tab.update({key_i:{'key':'version','val':fstr}})

        if len(conf_tab)>0:
            new_conf = {}
            for tab_i in conf_tab:
                tab_item = conf_tab[ tab_i ]
                new_conf.setdefault(tab_item['key'],tab_item['val'])

            with open(self.config_py, 'w') as fso:
                fso.write('newconfig=' + str(new_conf))
    