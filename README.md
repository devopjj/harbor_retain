# harbor_retain

Harbor 仓库维护工具

- 

### 功能说明

```sh
|-- 17copyto20.sh
|-- README.md
|-- getHarborimg.py
|-- harbor17-retain.py
|-- harbor2-retain.py
`-- harborclient_modify_v2_0.py
```

### 安装

**安装 Python 3**

CentOS7

```sh
$ sudo yum install python3
$ pip install -r requirements.txt
```

Debian/Ubuntu

```sh
$ sudo apt install python3.7-venv
$ pip install -r requirements.txt
```



### 使用说明

#### harbor17_retain.py

配置

```sh
# harbor api interface
api_url = "https://`xxx.xxx.xxx`/api"  # xxx.xxx.xxx , replaced with the url of harbor
# Login ,change username and password
login = HTTPBasicAuth('`USERNAME`', '`PASSWORD`') 
# exclude the projects

exclude = ['`proj1`', '`proj2`', '`proj3`''] 
# Number of images to keep
keep_num = `20`
```

**运行清理脚本**

```sh
$ python harbor17-retain.py
```

#### harbor2_retain.py

Harbor 2 本身已有自带API及 Retent Rule 可自动清理镜像版本数量，这个脚本或许也能帮助维护工作。

- 依时间先后次序保留固定数量的镜像版本，超过设定的则删除。
- 测试使用环境为：
  - Python 3.7.3
  - Harbor v2.0.2-e91b4ff1

**修改配置参数：**

```sh
# harbor api interface
api_url = "https://xxx.xxx.xxx/api"  # xxx.xxx.xxx部分自行更换为harbor首页url
# Login ,change username and password
login = HTTPBasicAuth('USERNAME', 'PASSWORD')   # 自行更改用户名，密码
# 需要排除的项目组，自行根据情况更改，或为空
exclude = ['k8s', 'basic', 'library']    # 自行更改需排除项目组，也可以删除为空; 例:exclude = ['k8s', 'basic', 'library']
# 仓库下版本过多，需保留的最近版本数量
keep_num = 10
# 启动Start the engine
main(api_url=api_url, login=login, num=keep_num, exclude=exclude)
```

**运行清理脚本**

```sh
$ python harbor2-retain.py
```

#### getHarbor17img.py

**修改配置参数：**

```sh
harbor17_url = 'xxx.xxx.xxx' # xxx.xxx.xxx部分自行更换为harbor首页url
harbor2_url = 'yyy.yyy.yyy' #  yyy.yyy.yyy部分自行更换为harbor首页url
api_url = 'http://{}/api'.format(harbor17_url) 
# Login ,change username and password
login = HTTPBasicAuth('admin', 'Harbor12345')   # 自行更改用户名，密码
# 需要排除的项目组，自行根据情况更改，或为空
exclude = ['library', 'dev', 'test' , 'release', 'fat']
# 清单存放档名
imglist = 'harbor17-20-img.lst'
# 仓库下版本过多，需保留的最近版本数量
# 0代表不限制
keep_num = 15
```

**运行清理脚本**

```sh
python getHarbor17img.py
```

harbor17-20-img.lst 清单内容格式如下，将提供**17copyto20.sh**进行复制时读取用。

```sh
base/centos7-java chatroom <harbor17>/base/centos7-java:devr01 <harbor2_url>/base/centos7-java:devr01
```

#### 17copyto20.sh

```sh
# 镜像清单档名
lst=/root/harbor17-img.lst
# Harbor 1.7
harbor17_url=harbor17.mydomain
harbor2_url=harbor2.mydomain
# .local_img产生方式：运行 getHarborimg.py

# 本地镜像列表暂存档 
local_img=/root/.local_img
```

**运行清理脚本**

```sh
$ chmod +x 17copyto20.sh
$ ./17copyto20.sh
```



### 问题排解

If you encounter the problem regarding to X509, try to fix with the following command.
CentOS 7

```
$ cp foo.crt /etc/pki/ca-trust/source/anchors/
$ update-ca-trust
```

