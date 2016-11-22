
# 用 Python 完成 Android apk 的编译打包

* Github地址：[https://github.com/Werb/AutoSecret](https://github.com/Werb/AutoSecret)

### 吐槽
* 其实当我写完之后，发现并没有什么卵用233
* 我最一开始想的是每一次在 Github 上发现好玩的 Android 应用，都要下载下来，然后 Gradle build 老半天，其中还要改一些参数，要是直接能装到手机上运行该多好
* 所以我就想，如果能写一个脚本，直接完成这些操作那就好了
* 虽然以前没接触过 Python ，但我知道这是一个很牛逼的语言啊，那就试着来写一写吧
* 实现的方法有很多，你可以用 java 或者直接 command-line , 但我就是想用 python

### 执行流程
1. 从 Github 上拉代码（zip包）下来
2. 解压 zip 包
3. Gradle build
4. adb install

### 使用方法
```
[app]
sdk_dir = /Users/admin/Wanbo/code/android/sdk
git_download_name = Werb/GankWithZhihu
assembleRelease = False

[dir]
base_file_dir = /Users/admin/Desktop
adb_dir =  /Users/admin/Werb/code/android/sdk/platform-tools/adb
gradle_dir = /users/admin/werb/code/gradle-2.14.1/bin
dir_name = AutoSecret
code_dir_name = SourceCode
apk_dir_name = Apk
code_zip_name = GankWithZhihu
```
在 auto.config 你要填
1. sdk 路径
2. Gradle 路径
3. adb 路径
4. 要下载的仓库名称
5. 下载到本地的路径

然后跑脚本就可以啦

是不是觉得很麻烦？ 我也是这样觉得的...但自己挖的坑...我不跳谁跳...

### 有哪些坑
* 如果 Gradle 和 abd 都是全局的，配置到环境变量里的话，就不用设置路径的，直接执行就好
* 如果项目中 buildToolsVersion 你本地没有的话，脚本是执行不成功的，所以你最好各个版本下载全
* 所以写完之后我发现这真的没什么卵用


 ### 剩下的代码
 ```python
 # !/user/bin.env python3
# -*- coding: utf-8 -*-

# 1.配置阶段

import os
import json
import requests
import zipfile

try:
  import configparser
except ImportError:
  import ConfigParser

Auto_config_path = os.path.dirname(__file__) + '/auto.config'

try:
  cf = configparser.ConfigParser()
  print('python3')
except Exception as e:
  cf = ConfigParser.ConfigParser()
  print('python2')

# 读取配置文件
cf.read(Auto_config_path)

sdk_dir = cf.get('app', 'sdk_dir')
git_download_name = cf.get('app', 'git_download_name')
assembleRelease = cf.getboolean('app', 'assembleRelease')
git_download_url = 'https://codeload.github.com/' + git_download_name + '/zip/master'


# 设置目录
base_file_dir = cf.get('dir', 'base_file_dir')
dir_name = cf.get('dir', 'dir_name')
code_dir_name = cf.get('dir', 'code_dir_name')
apk_dir_name = cf.get('dir', 'apk_dir_name')
code_zip_name = cf.get('dir', 'code_zip_name') + ".zip"
adb_dir = cf.get('dir', 'adb_dir')
gradle_dir = cf.get('dir', 'gradle_dir')

file_dir = base_file_dir + '/' + dir_name
code_dir = file_dir + '/' + code_dir_name
apk_dir = file_dir + "/" + apk_dir_name


# 2.下载源码

# 下载zip源码

if not os.path.exists(file_dir):
  os.mkdir(file_dir)
os.chdir(file_dir)
if not os.path.exists(code_dir):
  os.mkdir(code_dir)
if not os.path.exists(apk_dir):
  os.mkdir(apk_dir)
os.chdir(code_dir)

def cleanFile(targetDir):
  for file in os.listdir(targetDir):
      targetFile = os.path.join(targetDir, file)
      if os.path.isfile(targetFile):
          os.remove(targetFile)

cleanFile(code_dir)

print('下载地址: ' + git_download_url)
print('下载中...')
response = requests.get(git_download_url)
with open(code_zip_name, "wb") as code:
  code.write(response.content)
print(response.status_code)
if response.status_code == 200:
  print('下载完成！')
else:
  print('下载失败！')

# 解压zip包
z = zipfile.ZipFile(code_zip_name, 'r')
zip_name = z.namelist()[0]
try:
  for file in z.namelist():
      z.extract(file, code_dir)
  print('解压完成！')
except Exception as e:
  print('解压失败！')

# 生成local.properties文件
code_dir = code_dir + "/" + zip_name
def createLocalPropertiesFile(sourceDir,fileName,root_sdk_dir):
  if not os.path.exists(sourceDir):
      return

  fileDir = sourceDir + '/' + fileName

  if os.path.exists(fileDir):
      return

  f = open(fileDir, 'w')
  f.write('sdk.dir=' + root_sdk_dir)
  f.close()

createLocalPropertiesFile(code_dir, 'local.properties',  sdk_dir)

# 3. 打包

os.chdir(code_dir)
# os.system('chmod 777 gradlew')

print('gradle clean')
os.system(gradle_dir + ' clean')
print('gradle assemble, generate apk')

if assembleRelease:
  print('assembleRelease apk')
  os.system(gradle_dir + ' assembleRelease')
else:
  print('assembleDebug apk')
  os.system(gradle_dir + ' assembleDebug')

print('Generate apk finish!')

# 复制apk
def moveApk(sourceDir,  targetDir):
  if not os.path.exists(sourceDir):
      return

  for file in os.listdir(sourceDir):
       sourceFile = os.path.join(sourceDir,  file)
       targetFile = os.path.join(targetDir,  file)
       if os.path.isfile(sourceFile) and ('unaligned' not in os.path.basename(sourceFile)):
           open(targetFile, "wb").write(open(sourceFile, "rb").read())

source_apk_dir = code_dir + '/' + 'app/build/outputs/apk'

if os.path.exists(source_apk_dir):
  moveApk(source_apk_dir, apk_dir)

print('apk 复制成功！')

# 安装apk
print('abd install')
os.system(adb_dir + ' install ' + apk_dir + "/app-debug.apk")
print('安装成功！')
 ```
### 其实还是有收获的
* 这一次真的很系统的知道了 Android 应用是如何通过 Gradle 来完成打包的
* Python 初体验，真的是一个很炫酷的语言，同样功能简直比用 Java 来写少了N倍代码
* 很多轮子之所以造出来，就是因为某一个程序员很懒，我为什么要重复做这些事情，干脆造一个轮子只写一遍算了
* 当然我这个不算轮子，只是单纯的想写一写
* 接下来用 Python 写一个多渠道打包的脚本，这个还是有点用的
* 如果你看到了这里，那就去给一个 star 呀

## Contact Me
* Email：1025004680@qq.com
* Weib：[UMR80](http://weibo.com/singerwannber )
* GitHub:[Werb](https://github.com/Werb)
* Blog：[Werb's Blog](http://werb.github.io/)
* Stackoverflow：[Werb](http://stackoverflow.com/users/6596737/werb?tab=profile)
