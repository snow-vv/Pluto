#!/bin/sh

# 
# 要求：
# CentOS 7+
# Python 3.6+ (系统自带即可)
# 
# 安装目录： /opt/django-idcops/
# 默认端口号： 18113 (gunicorn)，参数：SrvPort
# idcops 版本： develop 或 master，参数：VERSION

WorkDir=/opt
[ -d ${WorkDir} ]||mkdir -p ${WorkDir}

VERSION=master
SrvAddr=0.0.0.0
SrvPort=18113

# gunicorn logfile and pid file
ProjDir=${WorkDir}/django-idcops
LogFile=${ProjDir}/logs/idcops.log
PidFile=${ProjDir}/run/idcops.pid

# Install system dependent packages
OS=$(cat /etc/os-release |grep -w '^ID'|awk -F= '{print $2}'|sed 's/\"//g')

case $OS in
  debian|ubuntu)
    apt install -y gcc python3 python3-dev libjpeg-dev openssl git
    ;;
  centos|fedora|rhel)
    yum install -y gcc python3-devel openssl git
    ;;
  alpine)
    apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev \
      tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev jpeg g++ openssl \
      gcc python3 python3-dev git
    ;;
  *)
    echo "unknow os ${OS}, exit!"
    exit 1
    ;;
esac


# 下载项目放到 /opt/ 目录下，最终项目目录为： /opt/django-idcops/
cd ${WorkDir}
git clone -b ${VERSION} https://gitee.com/wenvki/django-idcops.git
cd ${ProjDir}

# Check install.lock file exists
if [ -f 'install.lock' ];then
  echo "install.lock is already exists."
  exit 1
fi

# Check db.sqlite3 file exists
if [ -f 'db.sqlite3' ];then
  COMMAND="\cp -raf db.sqlite3 db.sqlite3.save-$(date +'%F')"
  echo "db.sqlite3 is already exists, will backup to db.sqlite3.save-$(date +'%F') ."
  eval $COMMAND
fi

VIRTUALENV="${ProjDir}/env"

which python3
if [ $? -ne 0 ];then
  echo "Need install python3 version."
  exit 1
fi

# Remove the existing virtual environment (if any)
if [ -d "$VIRTUALENV" ]; then
  COMMAND="\rm -rf ${VIRTUALENV} db.sqlite3"
  echo "Removing old virtual environment..."
  eval $COMMAND
else
  WARN_MISSING_VENV=1
fi


# Create a new virtual environment
COMMAND="/usr/bin/python3 -m venv ${VIRTUALENV}"
echo "Creating a new virtual environment at ${VIRTUALENV}..."
eval $COMMAND || {
  echo "--------------------------------------------------------------------"
  echo "ERROR: Failed to create the virtual environment. Check that you have"
  echo "the required system packages installed and the following path is"
  echo "writable: ${VIRTUALENV}"
  echo "--------------------------------------------------------------------"
  exit 1
}


# Activate the virtual environment
. ${VIRTUALENV}/bin/activate


# Install necessary system packages
COMMAND="pip install wheel -i https://mirrors.aliyun.com/pypi/simple"
echo "Installing Python system packages ($COMMAND)..."
eval $COMMAND || exit 1

# Install requirement packages
COMMAND="pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple"
echo "Installing Python requirement packages ($COMMAND)..."
eval $COMMAND || exit 1

# COMMAND="pip install -r requirements-prod.txt -i https://mirrors.aliyun.com/pypi/simple"
# echo "Installing Python requirement prod packages ($COMMAND)..."
# eval $COMMAND || exit 1


# settings secret key
SECRET_KEY=$(openssl rand -base64 37|cut -b 1-50)
NEW_SECRET_KEY="SECRET_KEY='${SECRET_KEY}'"
sed -i "/^SECRET_KEY/c ${NEW_SECRET_KEY}" idcops_proj/settings.py

# settings databases
# Use sqlite3 by default
# migrate
python manage.py makemigrations
python manage.py migrate

# collect static files
python manage.py collectstatic --no-input

# create django super user
UserName=admin
UserEmail=admin@idcops.cn
UserPass=$(openssl rand -base64 12)
ImportUser="from django.contrib.auth import get_user_model; User = get_user_model();"
DeleteUser="User.objects.filter(username='${UserName}').delete();"
CreateUser="User.objects.create_superuser('${UserName}', '${UserEmail}', '${UserPass}')"
echo "${ImportUser} ${DeleteUser} ${CreateUser}" | python manage.py shell
echo -e "用户名：${UserName}\n用户密码：${UserPass}"
echo -e "账户密码可以查看 install.log 文件"

echo -e "SECRET_KEY: ${SECRET_KEY}\n" > install.log
echo -e "Server: http://${SrvAddr}:${SrvPort}/\nUsername: ${UserName}\nPassword: ${UserPass}\nEmail: ${UserEmail}" >> install.log
echo -e "Server: http://${SrvAddr}:${SrvPort}/\nUsername: ${UserName}\nPassword: ${UserPass}\nEmail: ${UserEmail}" 
touch install.lock

RUN_SERVER="nohup ${VIRTUALENV}/bin/gunicorn --workers 3 \
  --bind ${SrvAddr}:${SrvPort} \
  --pid ${PidFile} \
  --log-file ${LogFile} \
  --access-logfile ${LogFile} \
  --pythonpath ${ProjDir} \
  idcops_proj.wsgi:application > /dev/null 2>&1 &"

eval ${RUN_SERVER}
