#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' +-+-+-+
    |2|.|0|
    +-+-+-+
    本脚本适用于清理释放harbor镜像仓库空间；
    此脚本基于harbor 2.0.2版本编写；
    harbor 1.x 版本不适用；
    修改配置4个项目
    host：harbr url
    user：登入帐号（管理权限）
    password: 登入密码
    prj_exclude： 排除专案列表
'''

import os
from time import sleep, time
import harborclient_modify_v2_0

class GetHarborApi(object):
    def __init__(self, host, user, password, protocol, prj_exclude, keep_num):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol
        self.prj_exclude = prj_exclude
        self.keep_num = int(keep_num)

        self.client = harborclient_modify_v2_0.HarborClient(self.host, self.user, self.password,
                                 self.protocol, self.prj_exclude, self.keep_num)

    def main(self):
        start = time()
        try:
            self.client.get_expired_artifacts()
            self.client.del_artifacts()
            self.client.logout()
            print("所有操作运行完成！")
            end = time()
            allTime = end - start
            print("运行结束共耗时:{:.2f}s".format(allTime))
        except:
            end = time()
            allTime = end - start
            #traceback.print_exc()
            print('清理出错！')
            print("运行结束共耗时:{:.2f}s".format(allTime))

if __name__ == '__main__':
    host = "xxx.xxx.xxx"
    user = "xxx"
    # 自行更改需排除项目组，也可以删除为空; 例:exclude = ['k8s', 'basic', 'library']
    prj_exclude = ['prj1', 'prj2', 'prj3']    
    # 仓库下版本过多，需保留的最近版本数量
    keep_num = "2"
    password = "********"
    protocol = "https"
    cline_get = GetHarborApi(host, user, password, protocol,prj_exclude, keep_num)
    cline_get.main()
    
