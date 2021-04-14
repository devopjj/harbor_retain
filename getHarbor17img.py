#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''本脚本适用于抓取 harbor 1.7.0 镜像仓库之镜像列表清单

    '''

import json
import os
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
# suppress SSL Warnings
requests.packages.urllib3.disable_warnings()

from tqdm import tqdm
import dateutil.parser as dp
from time import sleep, time
import traceback

class Harbor(object):
    def __init__(self, harbor17_url, harbor2_url, user, num, exclude, imglist):
        """
        初始化一些基本参数
        :param auth: login password authority management
        :param head: change user-agent
        :param url: harbor server api url
        :param project_exclude: Exclude project team
        :param num_limit: Limit the number of retained versions
        :param project_special: project dict id and repo total
        :param project_state: project dict name and id
        :param repo_state: repo dict name and tag total
        :param repo_dispose: Count the number of tag processing
        :param tag_state: tag dict repo_name and tag
        :prram imglist: image list files
        """
        self.auth = user
        self.head = {"user_agent": "Mozilla/5.0"}
        self.harbor17_url = harbor17_url
        self.harbor2_url = harbor2_url
        self.url = 'http://{}/api'.format(harbor17_url)
        self.project_exclude = exclude
        self.imglist = imglist
        self.num_limit = int(num)
        self.project_special = {}
        self.project_state = {}
        self.repo_state = {}
        self.repo_dispose_count = 0
        self.tag_state = {}

    def setting(self):
        self.session = requests.session()
        self.session.auth = self.auth
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        self.session.keep_alive = False

    def list_project(self):
        print("list_project")

        try:
            r_project = self.session.get("{}/projects".format(self.url), headers=self.head,verify=False)
            r_project.raise_for_status()
            # 将得到的文本转换格式
            project_data = json.loads(r_project.text)
            for i in project_data:
                # 项目组名称
                project_name = i.get('name')
                # 项目组id
                project_id = i.get('project_id')
                # 项目组仓库
                project_repo = i.get('repo_count')
                print(project_name,"<=>", self.project_exclude)
                if project_name in self.project_exclude:
                    continue
                # 利用一个字典将项目名称与id对应起来
                self.project_state[project_name] = project_id
                # 由于请求限制，另外用一个字典,对应id于repo总数
                self.project_special[project_id] = project_repo
                print("\033[0;32m项目名称:{}\t项目编号:{}\t项目下仓库统计:{}\033[0m".format(project_name, project_id, project_repo))
            print("\033[0;36mproject:项目组对应id列表:{}\033[0m".format(self.project_state))
            print("\033[0;36mproject:项目id对应仓库数:{}\033[0m".format(self.project_special))
        except:
            traceback.print_exc()
            raise

    def list_repo(self):
        try:
            for a in self.project_state.keys():
            #for a in ['base']:
                # 排除部分项目组
                if a not in self.project_exclude:
                    id = self.project_state.get(a)
                    # print(id)
                    # 由于请求限制，得出需请求的次数，整除+1
                    number = self.project_special.get(id) // 100 + 1
                    for i in range(number):
                        page = i + 1
                        r_repo = self.session.get(
                            "{}/repositories?project_id={}&page={}&page_size=100".format(self.url, id, page),
                            headers=self.head)
                        # 将得到的文本结果转换格式
                        repo_data = json.loads(r_repo.text)
                        for r in repo_data:
                            repo_id = r.get('id')
                            repo_name = r.get('name')
                            tag_count = r.get('tags_count')
                            # 利用字典将仓库名称与tag总量对应起来
                            self.repo_state[repo_name] = tag_count
            print("\033[0;31mrepo:排除部分项目组后，需过滤处理的仓库总量为:{}\033[0m".format(len(self.repo_state)))

        except:
            traceback.print_exc()
            raise

    def list_tag(self):
        try:
            # n 为repo 仓库名字
            fp = open( self.imglist, "w")
            for n in self.repo_state.keys():
                r_tag = self.session.get('{}/repositories/{}/tags'.format(self.url, n))
                tag_data = json.loads(r_tag.text)
                tag_dict = {}
                #sort json,以时间排序
                tag_sorted = sorted(tag_data, key=lambda k: k['created'], reverse=True)
                #print(tag_sorted)
                tag_id=1
                tagname_list = []
                # 列出原仓库所有的镜像
                for r_tag in tag_sorted:
                    # 只下载限制笔数内的仓库镜像，继续往下走
                    if tag_id <= self.num_limit or self.num_limit == 0:
                        img17 = '%s/%s:%s' % (self.harbor17_url,n,r_tag['name'])
                        img20 = img17.replace(harbor17_url, harbor2_url)
                        fp.write(n + ' '+ r_tag['name']+ ' ' + img17+' ' +img20 + '\n')
                        name = r_tag['name']
                        tagname_list.append(name)
                        print(tag_id,"将会下载",img20)                            
                        tag_id=tag_id+1 
                self.tag_state[n] = tagname_list
                self.repo_dispose_count += len(tagname_list)

            fp.close()                     
                       
        except:
            traceback.print_exc()
            raise

def main(harbor17_url, harbor2_url, login, num, exclude, imglist):
    start = time()
    try:
        # begin开始
        har = Harbor(harbor17_url=harbor17_url, harbor2_url=harbor2_url, user=login, num=num, exclude=exclude, imglist=imglist)
        # 配置
        har.setting()
        # 列出项目组
        har.list_project()
        # 列出repo仓库
        har.list_repo()
        # 列出tag版本
        har.list_tag()
        # 下载不保留版本
        #har.del_tag()
        # 回收存储
        # har.volume_recycle()
        print("所有操作运行完成！")
        end = time()
        allTime = end - start
        print("运行结束共耗时:{:.2f}s".format(allTime))
    except:
        end = time()
        allTime = end - start
        #traceback.print_exc()
        print('复制镜像出错！')
        print("运行结束共耗时:{:.2f}s".format(allTime))


if __name__ == '__main__':
    # harbor api interface
    harbor17_url = 'harbor.xz.com'
    harbor2_url = 'harbor2.xz.com'
    api_url = 'http://{}/api'.format(harbor17_url)  # xxx.xxx.xxx部分自行更换为harbor首页url
    # Login ,change username and password
    login = HTTPBasicAuth('opuser', 'Harbor12345')   # 自行更改用户名，密码
    # 需要排除的项目组，自行根据情况更改，或为空
    #exclude = ['library', 'dev', 'fat' ,'aisport', 'ccd', 'release', 'master-fat', 'beta']    # 自行更改需排除项目组，也可以下载为空; 例:exclude = ['k8s', 'basic', 'library']
    exclude = ['library', 'dev', 'test' ,'aisport', 'ccd', 'release', 'master-fat', 'beta']
    # 清单存放档名
    imglist = 'harbor17-20-img.lst'
    # 仓库下版本过多，需保留的最近版本数量
    # 0代表不限制
    keep_num = 15
    # 启动Start the engine
    main(harbor17_url=harbor17_url, harbor2_url=harbor2_url, login=login, num=keep_num, exclude=exclude,imglist=imglist)
