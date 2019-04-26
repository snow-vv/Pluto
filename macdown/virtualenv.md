##创建python3虚拟环境

###1.先安装环境缺少的包(root用户下)
```
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel
```
```
yum install readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
```

###2. 安装python环境(root用户下)
```
yum -y groupinstall development
```
```
wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz
```
```
tar xJf Python-3.6.0.tar.xz
```
```
cd Python-3.6.0
```
```
./configure && make && make install
```

###3.安装virtualenvwrapper
```
pip install virtualenv && pip install virtualenvwrapper
```
###4、配置环境变量
```
vim ~/.bashrc
添加
WORKON_HOME=/srv/envs
source /usr/bin/virtualenvwrapper.sh

source ~/.bashrc
```
###5、创建虚拟环境
```
mkvirtualenv Pluto --python=/usr/local/bin/python3.6
```
