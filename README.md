# harbor_retain

### Intro

Delete images of Harbor depending on the specific **keep_num ** of docker images for each project.

Images are sorted order by created time.

###  Install

OS: CentOS7

**Python 3**

```sh
$ yum install python3
```

**Python pip insall** 

```sh
$ pip3 install python-dateutil tqdm requests
```
### Configure

\# harbor api interface
api_url = "https://`xxx.xxx.xxx`/api"  # xxx.xxx.xxx , replaced with the url of harbor
\# Login ,change username and password
login = HTTPBasicAuth('`USERNAME`', '`PASSWORD`') 
\# exclude the projects
exclude = ['`proj1`', '`proj2`', '`proj3`''] 
\# Number of images to keep
keep_num = `20`

**Harbor x509 Certs** 

If you encounter the problem regarding to X509, try to fix with the following command.
CentOS 7

```
$ cp foo.crt /etc/pki/ca-trust/source/anchors/
$ update-ca-trust
```
