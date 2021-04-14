#!/usr/bin/env python3
# -*- coding=utf8 -*-

import os
import logging
import traceback
from tqdm import tqdm
from time import sleep
import requests
# suppress SSL Warnings
requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)


class HarborClient(object):
    def __init__(self, host, user, password, protocol, prj_exclude, num_limit):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol
        self.project_exclude = prj_exclude
        self.num_limit = num_limit
        self.repo_dispose_count = 0

        # 第一次get请求，获取 cookie 信息
        self.cookies, self.headers = self.get_cookie()

        # 获取登陆成功 session
        self.session_id = self.login()

        # 把登陆成功的 sid值 替换 get_cookie 方法中 cookie sid值，用于 delete 操作
        self.cookies_new = self.cookies
        self.cookies_new.update({'sid': self.session_id})


    # def __del__(self):
    #     self.logout()

    def get_cookie(self):
        response = requests.get("{0}://{1}/c/login".format(self.protocol, self.host),verify=False)
        csrf_cookie = response.cookies.get_dict()
        headers = {'X-Harbor-CSRF-Token': csrf_cookie['__csrf']}
        return csrf_cookie, headers

    def login(self):
        login_data = requests.post('%s://%s/c/login' %
                                   (self.protocol, self.host),
                                   data={'principal': self.user,
                                         'password': self.password}, cookies=self.cookies, 
                                         headers=self.headers,verify=False)

        if login_data.status_code == 200:
            session_id = login_data.cookies.get('sid')

            logging.debug("Successfully login, session id: {}".format(
                session_id))
            return session_id
        else:
            logging.error("Fail to login, please try again")
            os._exit(-1)
            return None

    def logout(self):
        path = '%s://%s/c/logout' % (self.protocol, self.host)
        requests.get(path,
                     cookies={'sid': self.session_id},
                     verify=False)
        logging.debug("Successfully logout")

    # GET /statistics
    def get_statistics(self):
        path = '%s://%s/api/v2.0/statistics' % (self.protocol, self.host)
        response = requests.get(path, 
                                    cookies=self.cookies_new,
                                    headers=self.headers,
                                    verify=False)
        if response.status_code == 200:
            print("Login {} successful!".format(self.user))
            logging.debug("Successfully Login: {}".format(
                self.user))
            return(True)
        else:
            logging.error("Fail to Login: {}".format(self.user))
        return None       
    # GET /projects
    def get_projects(self, project_name=None, is_public=None):
        # TODO: support parameter
        result = []
        page = 1
        page_size = 15

        while True:
            path = '%s://%s/api/v2.0/projects?page=%s&page_size=%s' % (self.protocol, self.host, page, page_size)
            response = requests.get(path,
                                    cookies={'sid': self.session_id},
                                    verify=False)
            if response.status_code == 200:
                logging.debug("成功提取专案清单: {}".format(
                    result))
                if isinstance(response.json(), list):
                    result.extend(response.json())
                    page += 1
                else:
                    break
            else:
                logging.error("提取专案清单失败")
                result = None
                break
        return result

    # GET /projects/{project_name}/repositories
    def get_repositories(self, project_name, query_string=None):
        # TODO: support parameter
        result = []
        page = 1
        page_size = 15

        while True:
            path = '%s://%s/api/v2.0/projects/%s/repositories?page=%s&page_size=%s' % (
                self.protocol, self.host, project_name, page, page_size)
            response = requests.get(path,
                                    cookies={'sid': self.session_id},
                                    verify=False)
            if response.status_code == 200:
                logging.debug(
                    "Successfully get repositories with name: {}, result: {}".format(
                        project_name, result))
                if len(response.json()):
                    result.extend(response.json())
                    page += 1
                else:
                    break
            else:
                logging.error("Fail to get repositories result with name: {}".format(
                    project_name))
                result = None
                break
        return result

    # GET /projects/{project_name}/repositories/{repository_name}/artifacts?with_tag=true&with_scan_overview=true&with_label=true&page_size=15&page=1
    def get_repository_artifacts(self, project_name, repository_name):
        result = []
        page = 1
        page_size = 15

        while True:
            path = '%s://%s/api/v2.0/projects/%s/repositories/%s/artifacts?with_tag=true&with_scan_overview=true&with_label=true&page_size=%s&page=%s' % (
                self.protocol, self.host, project_name, repository_name, page_size, page)
            response = requests.get(path,
                                    cookies={'sid': self.session_id}, 
                                    verify=False, 
                                    timeout=60)
            if response.status_code == 200:
                logging.debug(
                    "Successfully get repositories artifacts with name: {}, {}, result: {}".format(
                        project_name, repository_name, result))
                if len(response.json()):
                    result.extend(response.json())
                    page += 1
                else:
                    break
            else:
                logging.error("Fail to get repositories artifacts result with name: {}, {}".format(
                    project_name, repository_name))
                result = None
                break
        return result

    # DELETE /projects/{project_name}/repositories/{repository_name}
    def delete_repository(self, project_name, repository_name, tag=None):
        # TODO: support to check tag
        # TODO: return 200 but the repo is not deleted, need more test
        result = False
        path = '%s://%s/api/v2.0/projects/%s/repositories/%s' % (
            self.protocol, self.host, project_name, repository_name)
        response = requests.delete(path, 
                                    cookies=self.cookies_new,
                                    headers=self.headers,
                                    verify=False)
        if response.status_code == 200:
            result = True
            print("Delete {} successful!".format(repository_name))
            logging.debug("Successfully delete repository: {}".format(
                repository_name))
        else:
            logging.error("Fail to delete repository: {}".format(repository_name))
        return result

    # Get /projects/{project_name}/repositories/{repository_name}/artifacts/{reference}/tags
    def get_repository_tags(self, project_name, repository_name, reference_hash):
        result = None
        path = '%s://%s/api/v2.0/projects/%s/repositories/%s/artifacts/%s/tags' % (
            self.protocol, self.host, project_name, repository_name, reference_hash)
        response = requests.get(path,
                                cookies={'sid': self.session_id},
                                verify=False,
                                timeout=60)
        if response.status_code == 200:
            result = response.json()
            logging.debug(
                "Successfully get tag with repository name: {}, result: {}".format(
                    repository_name, result))
        else:
            logging.error("Fail to get tags with repository name: {}".format(
                repository_name))
        return result

    # Del /projects/{project_name}/repositories/{repository_name}/artifacts/{reference}/tags/{tag_name}
    def del_repository_tag(self, project_name, repository_name, reference_hash, tag):
        result = False
        path = '%s://%s/api/v2.0/projects/%s/repositories/%s/artifacts/%s/tags/%s' % (
            self.protocol, self.host, project_name, repository_name, reference_hash, tag)
        response = requests.delete(path, 
                                    cookies=self.cookies_new, 
                                    headers=self.headers,
                                    verify=False)
        if response.status_code == 200:
            result = True
            print("Delete {} {} {} {} successful!".format(project_name, repository_name, reference_hash, tag))
            logging.debug(
                "Successfully delete repository project_name: {}, repository_name: {}, reference_hash: {}, tag: {}".format(
                    project_name, repository_name, reference_hash, tag))
        else:
            logging.error("Fail to delete repository project_name: {}, repository_name: {}, reference_hash: {}, tag: {}".format(
                project_name, repository_name, reference_hash, tag))
        return result

    # Del /projects/{project_name}/repositories/{repository_name}/artifacts/{reference}
    def del_artifacts_hash(self, project_name, repository_name, reference_hash):
        result = False
        path = '%s://%s/api/v2.0/projects/%s/repositories/%s/artifacts/%s' % (
            self.protocol, self.host, project_name, repository_name, reference_hash)
        response = requests.delete(path, 
                                    cookies=self.cookies_new, 
                                    headers=self.headers,
                                    verify=False)
        ##print(response)
        if response.status_code == 200:
            result = True
            print("项目: {} 仓库: {} 版本: {} 删除成功!".format(project_name, repository_name, reference_hash))
            logging.debug(
                "删除成功项目: {}, 仓库: {}, 版本: {}".format(
                    project_name, repository_name, reference_hash))
        else:
            logging.error("项目:  {}, 仓库:  {}, 版本:  {}".format(
                project_name, repository_name, reference_hash))
        return result

	# 列出过期要删除的仓库项目（版本）
    def get_expired_artifacts(self):
        print('列出全部专案')
        prj={}
        self.artifact_list = []
        try:
            
            for p in self.get_projects():
                project_id = p['project_id']
                project_name = p['name']
                prj[project_id] = project_name

                # 排除部分项目组
                if project_name in self.project_exclude:
                    continue

                print("\033[0;36m列出专案:{}\033[0m".format(project_name))
                
                for r in self.get_repositories(project_name):
                    repo_name = r['name'].replace(project_name+'/', '').replace('/','%252F')
                    ##repo_name = 'admin-merchant/1224'.replace('/','%252F')
                    # 列出 artifact
                    arti_prefix='{}/{}'.format(project_name, repo_name)
                    af_data = self.get_repository_artifacts(project_name, repo_name)
                    af_sorted = sorted(af_data, key=lambda k: k['extra_attrs']['created'], reverse=True)
                    af_id=1
                    
                    
                    print("\033[0;36m专案名称:{}\t项目编号:{}\t项目下仓库统计:{}\033[0m".format(project_name, repo_name, len(af_sorted)))
                    #print("\033[0;36mproject:项目id对应仓库数:{}\033[0m".format(self.project_special))
                    for a in af_sorted:
                        artifact_id = a['tags'][0]['artifact_id']
                        artifact_tags = a['tags'][0]['name']
                        artifact_digest = a['digest']
                        artifact_created = a['extra_attrs']['created']
                        # 超出保留數限制數的標記刪除
                        if af_id > self.num_limit:
                            ##/projects/{project_name}/repositories/{repository_name}/artifacts/{reference}
                            af_url='projects/{}/repositories/{}/artifacts/{}'.format(project_name, repo_name,artifact_digest)
                            print('{}[x]将会删除 {}:{}, created:{}'.format(af_id-self.num_limit,arti_prefix,artifact_tags,artifact_created.split('T')[0]))
                            self.artifact_list.append([project_name, repo_name, artifact_digest])
                        #else:
                            #print('{} 保留: {}:{}'.format(af_id,arti_prefix,artifact_tags ))
                        af_id=af_id+1                        
                    #print(self.artifact_list)
                    self.repo_dispose_count += len(self.artifact_list)
                    
                    ##break
                # loop project
                ##break
            
        except:
            traceback.print_exc()
            raise

    # 删除过期的镜像
    def del_artifacts(self):
        try:
            delete_total = 0
            del_faild = []
            if self.repo_dispose_count == 0:
                print("\033[0;34mdel:本次无需删除tag\033[0m")
            else:
                print("\033[0;34mdel:删除tag阶段耗时较长:请耐心等待\033[0m")
                pbar1 = tqdm(total=self.repo_dispose_count, unit='个', unit_scale=True)

                for af in self.artifact_list:
                    uri = '%s://%s/api/v2.0/%s' % (self.protocol, self.host, af)

                    prj = af[0]
                    repo = af[1]
                    ref = af[2]
                    #print('delete..{}/{}/{}'.format(prj, repo, ref))

                    try:
                        r_del = self.del_artifacts_hash(prj, repo, ref)
                        delete_total += 1
                        pbar1.update(1)
                    except:
                        print('del: {}仓库下删除版本号:{}失败！！！'.format(repo, ref))
                        del_faild.append(af)

                sleep(3)
                pbar1.close()
                print("\033[0;34mdel:需删除镜像已完成删除！ 共删除版本数量:{}个\033[0m".format(delete_total))
                print('删除失败共计：{}，删除失败的为：{}'.format(len(del_faild), del_faild))

        except:
            traceback.print_exc()
            raise                
                  