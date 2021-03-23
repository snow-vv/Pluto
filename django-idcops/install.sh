#!/bin/bash


cd "$(dirname "$0")"
VIRTUALENV="$(pwd -P)/env"

which python3
if [ $? -ne 0 ];then
  echo "Need install python3 version."
fi

# Remove the existing virtual environment (if any)
if [ -d "$VIRTUALENV" ]; then
  COMMAND="rm -rf ${VIRTUALENV} db.sqlite3"
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
source "${VIRTUALENV}/bin/activate"

# Install system dependent packages
yum install -y gcc python3-devel

# Install necessary system packages
COMMAND="pip install wheel -i https://mirrors.aliyun.com/pypi/simple"
echo "Installing Python system packages ($COMMAND)..."
eval $COMMAND || exit 1

# Install requirement packages
COMMAND="pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple"
echo "Installing Python requirement packages ($COMMAND)..."
eval $COMMAND || exit 1

COMMAND="pip install -r requirements-prod.txt -i https://mirrors.aliyun.com/pypi/simple"
echo "Installing Python requirement prod packages ($COMMAND)..."
eval $COMMAND || exit 1


# settings secret key
SECRET_KEY=$(openssl rand -base64 37|cut -b 1-50)
NEW_SECRET_KEY="SECRET_KEY='${SECRET_KEY}'"
sed -i "/^SECRET_KEY/c ${NEW_SECRET_KEY}" idcops_proj/settings.py

# settings databases
# Use sqlite3 by default
# migrate
source "${VIRTUALENV}/bin/activate"
mkdir -p media
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

# runserver 
SrvAddr='0.0.0.0'
# 0.0.0.0 默认侦听所有本机地址，或例如本机地址：192.168.7.77
SrvPort='8000'

echo -e "Server: http://${SrvAddr}:${SrvPort}/\nUsername: ${UserName}\nPassword: ${UserPass}\nEmail: ${UserEmail}" > install.log

python manage.py runserver ${SrvAddr}:${SrvPort}
