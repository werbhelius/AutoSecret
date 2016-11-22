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
os.system('chmod 777 gradlew')

print('gradlew clean')
os.system('./gradlew clean')
print('gradlew assemble, generate apk')

if assembleRelease:
    print('assembleRelease apk')
    os.system('./gradlew assembleRelease')
else:
    print('assembleDebug apk')
    os.system('./gradlew assembleDebug')

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