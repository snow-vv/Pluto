## 一键部署zabbix

###zabbix-server
```
#!/bin/bash
#zabbix-server
while(true)
do
echo "1、关闭防火墙和selinux"
echo "2、安装epel源"
echo "3、检查mysql,nginx,php,zabbix服务是否安装"
echo "4、安装nginx服务"
echo "5、安装php服务"
echo "6、安装mysql服务"
echo "7、安装zabbix服务"
echo "8、清理服务安装过程中的文件"
echo "9、退出"
read -p "please input a num:" n
case $n in
1)
echo -n "备份防火墙设置.................."
iptables -L >> /tmp/iptables.txt
systemctl stop firewalld #关闭防火墙服务
firewalld_status=`systemctl status firewalld | awk '{print $2}' | head -3 | tail -1`
if [ $firewalld_status = "inactive" ]
then
echo "防火墙服务已关闭"
iptables -L
else
echo "防火墙服务关闭失败，请查看日志分析原因"
exit 1
fi
systemctl disable firewalld #设置防火墙服务开机不启动
if [ $? -eq 0 ]
then
echo "成功设置防火墙不开机自动启动"
else
echo "操作失败，请查找原因"
exit 1
fi
if [ `getenforce` = "Enforcing" ]
then
setenforce 0 > /dev/null 2>&1 #手动临时关闭selinux
fi
sed -i 's/enforcing/disabled/g' /etc/selinux/config #永久关闭selinux，重启之后生效
;;
2)
#替换epel源
cd /etc/yum.repos.d/
if [[ `pwd` = "/etc/yum.repos.d" ]];then
echo "你已经在$PATH 目录下了"
mkdir backup
mv *.repo backup/
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo #下载epel源repo文件
mv backup/CentOS-Base.repo ./
else
echo "切换目录失败，请继续尝试"
exit 1
fi
sleep 1s
yum clean all && /usr/bin/yum makecache #清理旧缓存，创建新的缓存
;;
3)
NGINX=`rpm -qa | grep nginx | awk '{print $1}'` #检查nginx、mysql、php、zabbix服务是否安装
MYSQL=`rpm -qa | grep mariadb | awk '{print $1}'`
PHP=`rpm -qa | grep php | awk '{print $1}'`
ZABBIX=`rpm -qa | grep zabbix | awk '{print $1}'`
STATUS=($NGINX $MYSQL $PHP $ZABBIX) #设立数组STATUS，为卸载上述服务做准备
for status in ${STATUS[*]}
do
if [[ -n $status ]];then
yum -y remove $status #移除已安装的服务
else
exit 1
fi
done
echo "各软件没有安装，请执行安装"
;;
4)
yum -y install nginx >> /tmp/nginx.txt #安装nginx服务
if [[ `cat /tmp/nginx.txt | grep Error | awk -F ":" '{print $1}'` = "Error" ]] #检查服务是否成功安装，如果不成功，换成atomic源继续进行
then
wget http://www.atomicorp.com/installers/atomic
sh ./atomic
yum check-update
if [ $? -eq 0 ]
then
echo "atomic源安装成功"
fi
sleep 3s
yum -y install nginx
fi
systemctl start nginx.service #启动nginx服务
nginx_status=`systemctl status nginx | awk '{print $2}' | head -3 | tail -1`
if [ $nginx_status = "active" ] #检查nginx服务是否成功启动
then
echo "nginx服务启动成功，正在运行中。。。。。"
else
echo "nginx服务启动失败，请分析原因并解决"
exit 1
fi
NGINX_CONF=/etc/nginx/nginx.conf
mv $NGINX_CONF /etc/nginx/nginx.conf.bak
cat /root/nginx.conf > $NGINX_CONF #进行nginx配置文件的修改
systemctl restart nginx #重新启动nginx服务，加载配置文件
if [[ $? -eq 0 ]];then #判断服务重启是否成功
echo "nginx服务重启成功"
netstat -tlnp
else
echo "nginx服务重启失败，请检查配置文件是否正常"
exit 1
fi
;;
5)
packages=(php lighttpd-fastcgi php-cli php-mysql php-gd php-imap php-ldap php-odbc php-pear php-xml php-xmlrpc php-mbstring php-mcrypt php-mssql php-snmp php-soap)
for package in ${packages[*]}
do
if [ -n $package ];then
yum -y install $package #安装php的依赖包
else
echo "字符串为空，没有取到数组中的数值"
exit 1
fi
done
php_packages=(php-tidy php-common php-devel php-fpm php-mysql)
for php_package in ${php_packages[*]}
do
if [[ -z $php_package ]]; then
echo -n "字符串为空，没有取到数组中的数值，请查看相应的报错信息"
exit 1
else
yum -y install $php_package #安装php和所需组件使用php支持mysql、fastcgi模式
fi
done
sed -i 's/max_execution_time = 30/max_execution_time = 300/g' /etc/php.ini #修改zabbix相关参数max_execution_time
sed -i 's/max_input_time = 60/max_input_time = 300/g' /etc/php.ini #修改zabbix相关参数max_input_time
sed -i 's/post_max_size = 8M/post_max_size = 16M/g' /etc/php.ini #修改zabbix相关参数post_max_size
sed -i 's#;date.timezone =#date.timezone =Asia/shanghai#g' /etc/php.ini #修改zabbix相关参数date.timezone
sed -i '$a\cgi.fix_pathinfo = 1' /etc/php.ini #设置php支持pathinfo模式
sed -i '$a\extension=bcmath.so' /etc/php.ini #设置php支持bcmath模块
systemctl start php-fpm.service #重新启动php-fpm服务
php_status=`systemctl status php-fpm | awk '{print $2}' | head -3 | tail -1`
if [[ -n $php_status && $php_status = "active" ]]; then #判断php-fpm服务是否成功启动
echo "php-fpm服务已启动，目前正在运行中"
netstat -tlnp
chkconfig --levels 235 php-fpm on #设置php-fpm服务开机自动启动
sleep 2s
fi
;;
6)
yum -y install mariadb mariadb-server #yum安装mariadb数据库服务相关软件
sleep 2s
DB=`yum list installed | grep mariadb | awk -F "-" '{print $1}'`
if [[ -n $DB && $DB = "mariadb" ]];then #判断mairadb是否成功安装
echo "数据库安装成功"
fi
systemctl start mariadb.service #启动mariadb服务
sleep 1s
mariadb_status=`systemctl status mariadb.service | awk '{print $2}' | head -3 | tail -1`
if [[ -n $mariadb_status && $mariadb_status = "active" ]]; then #判断mariadb是否成功启动
echo -n "mariadb数据库已启动，目前运行状态一切正常"
netstat -tlnp
else
echo -n "mariadb数据库启动失败，请查找分析原因"
fi
#配置数据库，创建zabbix数据库
mysqladmin -u root password 123.com
mysql -u root -p123.com << DBS 2>/dev/null
show databases;
create database zabbix character set utf8 collate utf8_bin;
grant all on zabbix.* to zabbix@'localhost' identified by '123.com';
flush privileges;
DBS
;;
7)
wget http://repo.zabbix.com/zabbix/3.0/rhel/7/x86_64/zabbix-release-3.0-1.el7.noarch.rpm #下载zabbix安装源
rpm -ivh zabbix-release-3.0-1.el7.noarch.rpm #安装zabbix源的rpm包
rpm_zabbix=`rpm -qa | grep zabbix | awk -F "-" '{print $1}'`
if [[ $rpm_zabbix = "zabbix" ]]; then
echo "zabbix源已经安装完毕"
else
exit 1
fi
yum -y install zabbix-server-mysql zabbix-web-mysql #安装zabbix服务相关软件
if [[ $? -eq 0 ]]; then
echo "zabbix server端所需的安装包已经安装成功"
else
exit 1
fi
cd /usr/share/doc/zabbix-server-mysql-3*
zcat create.sql.gz | mysql -uzabbix -p123.com zabbix #将zabbix的所有表都导入到zabbix数据库
if [ $? -eq 0 ]; then
echo "成功将zabbix数据导入到mariadb数据库中"
else
echo "数据导出失败，请查清原因"
exit 1
fi
#配置zabbix_server.conf文件
zabbix=/etc/zabbix/zabbix_server.conf
cp $zabbix /etc/zabbix/zabbix_server.conf.bak
sed -i 's/# DBHost=localhost/DBHost=localhost/g' $zabbix
sed -i 's/# DBPassword=/DBPassword=123.com/g' $zabbix
systemctl start zabbix-server #启动zabbix服务
zabbix=`systemctl status zabbix-server | awk '{print $2}' | head -3 | tail -1`
if [[ $zabbix = "active" ]]; then
echo "zabbix-server服务启动成功，正在运行中...."
netstat -tlnp
else
echo "zabbix-server服务启动失败，请查看输出日志分析原因"
exit 1
fi
cp -r /usr/share/zabbix/ /usr/share/nginx/html/ #配置zabbix页面的文件
cd /usr/share/nginx/html/zabbix/conf
mv zabbix.conf.php.example zabbix.conf.php
;;
8)
#清理安装过程中产生的垃圾文件
rm -rf zabbix-release-3.0-1.el7.noarch.rpm
rm -rf /tmp/nginx.txt
rm -rf /tmp/iptables.txt
;;
9)
#查看服务端口
netstat -tlnp
break
;;
esac
done

```
###zabbix-agent
```
#!/bin/bash
#zabbix-agent安装脚本
install_release(){
if [[ -f /tmp/zabbix-release-3.0-1.el7.noarch.rpm ]];
then
echo "zabbix-release already exited"
else
wget http://repo.zabbix.com/zabbix/3.0/rhel/7/x86_64/zabbix-release-3.0-1.el7.noarch.rpm -P /tmp
rpm -ivh /tmp/zabbix-release-3.0-1.el7.noarch.rpm
fi
}
install_agent(){
agent_exist=`yum list installed | grep zabbix-agent | awk -F "." '{print $1}'`
if [[ -n $agent_exist && $agent_exist = "zabbix-agent" ]]; then
echo "zabbix-agent已安装，无需再次执行安装命令"
else
yum -y install zabbix-agent
if [[ $? -eq 0 ]]; then
echo "zabbix-agent安装成功"
else
echo "zabbix-agent安装失败，查看原因进行排错"
exit 1
fi
fi
}
#配置zabbix_agent.conf
configure_file(){
local agent=/etc/zabbix/zabbix_agentd.conf
cp $agent /etc/zabbix/zabbix_agentd.conf.bak
sed -i 's/Server=127.0.0.1/Server=192.168.0.86/g' $agent
sed -i 's/ServerActive=127.0.0.1/ServerActive=192.168.0.86/g' $agent
sed -i 's/Hostname=Zabbix server/Hostname=zabbix-server/g' $agent
systemctl start zabbix-agent
PORT=`netstat -tlnp | grep 10050 | awk -F ":" '{print $2}' | awk '{print $1}'`
if [[ $PORT -eq 10050 ]];
then
echo "zabbix-agent已经在运行中.............."
netstat -tlnp
else
echo "zabbix-agent服务启动失败，请仔细查找分析原因"
fi
}
install_all(){
alls=(install_release install_agent configure_file)
for all in ${alls[*]};
do
$all
sleep 5s
if [[ $? -eq 0 ]]; then
get_char(){
SAVEDSTTY=`stty -g`
stty -echo
stty cbreak
dd if=/dev/tty bs=1 count=1 2> /dev/null
stty -raw
stty echo
stty $SAVEDSTTY
}
echo ""
echo "Press any key to continue...or Press Ctrl+C to cancel"
char=`get_char`
echo "$all 执行成功，开始进行下一步操作"
else
echo "$all 执行失败，请查看原因"
exit 1
fi
done
}
main(){
install_all
rm -rf /tmp/zabbix-release-3.0-1.el7.noarch.rpm
}
main

```
###wordpress
```
#!/bin/bash
path1=/usr/local/php-7.1.9
path2=/usr/local/php
check_nginx(){
nginx=`rpm -qa | grep nginx | awk -F "-" '{print $1}' | head -1`
if [[ -z $nginx ]]; then
echo "nginx服务没有安装，系统内没有nginx"
read -p "请确认是否安装nginx，yes or no ?" n
if [[ $n = "yes" ]]; then
echo "start install nginx now"
sleep 2s
prepare_nginx
elif [[ $n = "no" ]]; then
echo "you have already canceled installation of nginx"
exit 1
else
echo "You have entered the wrong instruction, please re-enter as prompted"
fi
else
echo "nginx service has been exited"
get_char(){
SAVEDSTTY=`stty -g`
stty -echo
stty cbreak
dd if=/dev/tty bs=1 count=1 2> /dev/null
stty -raw
stty echo
stty $SAVEDSTTY
}
echo ""
echo "Press any key to continue...or Press Ctrl+C to cancel"
char=`get_char`
echo "继续开始接下来的服务安装"
fi
}
prepare_nginx(){
packages=(wget openssl* gcc gcc-c++ autoconf libjpeg libjpeg-devel libpng libpng-devel freetype freetype-devel libxml2 libxml2-devel zlib zlib-devel glibc glibc-devel glib2 glib2-devel bzip2 bzip2-devel ncurses ncurses-devel curl curl-devel e2fsprogs e2fsprogs-devel krb5 krb5-devel libidn libidn-devel openssl openssl-devel openldap openldap-devel nss_ldap openldap-clients openldap-servers make gd gd2 gd-devel gd2-devel libxslt libxslt-devel libaio libaio-devel)
nginx_user=`cat /etc/passwd | grep www`
for package in ${packages[*]}; do
if [[ -z `yum list installed | grep $package | head -1` ]]; then
echo "now! start install $package"
yum -y install $package
else
echo "$package has already been installed"
fi
done
if [[ -n ${nginx_user} ]];
then
exit 1
else
groupadd nginx
useradd -r -g nginx nginx
fi
install_nginx 2> /dev/null
}
systemctl_nginx(){
echo "[Unit]
Description=nginx - high performance web server
Documentation=https://nginx.org/en/docs/
After=network.target remote-fs.target nss-lookup.target
[Service]
Type=forking
PIDFile=/usr/local/nginx/logs/nginx.pid
ExecStartPre=/usr/local/nginx/sbin/nginx -t -c /usr/local/nginx/conf/nginx.conf
ExecStart=/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true
[Install]
WantedBy=multi-user.target"
}
install_nginx(){
local nginx_service=/usr/lib/systemd/system/nginx.service
wget http://nginx.org/download/nginx-1.13.5.tar.gz
if [[ $? -eq 0 ]]; then
echo "nginx deb has been downloaded successfully"
tar zxvf nginx-1.13.5.tar.gz
else
echo "nginx doesn't download"
fi
cd nginx-1.13.5
./configure --user=nginx --group=nginx --prefix=/usr/local/nginx
make && make install
if [[ -f $nginx_service ]]; then
rm -rf $nginx_service
systemctl_nginx > $nginx_service
else
systemctl_nginx > $nginx_service
fi
systemctl start nginx
}
install_php(){
debs=(gcc gcc-c++ openssl-devel zlib-devel libxml2-devel libjpeg-turbo-devel libiconv-devel freetype-devel libpng-devel gd-devel libcurl-devel libxslt-devel mhash mhash-devel mcrypt mcrypt-devel libmcrypt-devel)
for deb in ${debs[*]}; do
if [[ -n $deb ]]; then
yum -y install $deb
echo "install $deb successfully"
sleep 1s
else
echo "install $deb faild,please look for the reason"
exit 1
fi
done
wget https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.15.tar.gz
tar zxvf libiconv-1.15.tar.gz -C /usr/local/
if [[ $? -eq 0 ]]; then
cd /usr/local/libiconv-1.15/
./configure --prefix=/usr/local/libiconv
make && make install
else
echo "libiconv 库安装失败"
fi
wget http://php.net/distributions/php-7.1.9.tar.gz
tar zxvf php-7.1.9.tar.gz -C /usr/local/
if [[ $? -eq 0 ]];
then
cd $path1
./configure --prefix=$path2 --with-mysqli=mysqlnd --with-pdo-mysql=mysqlnd --with-mysqli=mysqlnd --with-iconv-dir=/usr/local/libiconv --with-freetype-dir --with-jpeg-dir --with-png-dir --with-zlib --with-libxml-dir=/usr --enable-xml --disable-rpath --enable-safe-mode --enable-bcmath --enable-shmop --enable-sysvsem --enable-inline-optimization --with-curl --with-curlwrappers --enable-mbregex --enable-fpm --enable-mbstring --with-mcrypt --with-gd --enable-gd-native-ttf --with-openssl --with-mhash --enable-pcntl --enable-sockets --with-xmlrpc --enable-zip --enable-soap --enable-short-tags --enable-zend-multibyte --enable-static --with-xsl --with-fpm-user=nginx --with-fpm-group=nginx --enable-ftp
make -j 4 && make install
fi
configure_php 2> /dev/null
service php-fpm start
}
configure_php(){
cp $path1/php.ini-production $path2/lib/php.ini
cp $path2/etc/php-fpm.conf.default $path2/etc/php-fpm.conf
cp $path1/sapi/fpm/init.d.php-fpm /etc/init.d/php-fpm
chmod 755 /etc/init.d/php-fpm
mv $path2/etc/php-fpm.d/www.conf.default $path2/etc/php-fpm.d/www.conf
}
install_mariadb(){
local mariadb=`rpm -qa | grep mariadb | awk '{print $1}' | head -1`
if [[ -z $mariadb ]]
then
yum -y install mariadb mariadb-server
else
yum -y remove mariadb*
yum -y install mariadb mariadb-server
fi
systemctl start mariadb
mysqladmin -u root password 123.com
mysql -u root -p123.com <<EOX
create database wordpress;
grant all privileges on *.* to root@'localhost' identified by '123.com' with grant option;
flush privileges;
EOX
}
install_wordpress(){
local config=/web/wordpress/wp-config.php
local dir=/web
if [[ -d $dir ]];
then
wget https://cn.wordpress.org/wordpress-4.9.4-zh_CN.tar.gz
tar zxvf wordpress-4.9.4-zh_CN.tar.gz -C /web
else
mkdir /web
wget https://cn.wordpress.org/wordpress-4.9.4-zh_CN.tar.gz
tar zxvf wordpress-4.9.4-zh_CN.tar.gz -C /web
fi
cp /web/wordpress/wp-config-sample.php $config
sed -i 's/database_name_here/wordpress/g' $config
sed -i 's/username_here/root/g' $config
sed -i 's/password_here/123.com/g' $config
sed -i 's/localhost/127.0.0.1/g' $config
nginx_conf > /usr/local/nginx/conf/nginx.conf
systemctl restart nginx
}
nginx_conf(){
echo "worker_processes 1;
events {
worker_connections 1024;
}
http {
include mime.types;
default_type application/octet-stream;
sendfile on;
keepalive_timeout 65;
server {
listen 80;
server_name localhost;
location / {
root /web;
index index.html index.php index.htm;
}
error_page 500 502 503 504 /50x.html;
location = /50x.html {
root html;
}
location ~ \.php$ {
root /web;
fastcgi_pass 127.0.0.1:9000;
fastcgi_index index.php;
include fastcgi_params;
}
}
}"
sed -i '24a\fastcgi_param SCRIPT_FILENAME /web$fastcgi_script_name;' /usr/local/nginx/conf/nginx.conf
}
install_all(){
local alls=(check_nginx install_php install_mariadb install_wordpress)
for all in ${alls[*]};
do
$all
netstat -tlnp
done
}
main(){
install_all
}
main

```

###mysql-bak
```
#!/bin/bash
#数据库数据备份脚本
source_profile(){
sed -i '$a\ZABBIX_MYSQL_USER=zabbix' /etc/profile
sed -i '$a\ZABBIX_MYSQL_PASSWORD=123.com' /etc/profile
sed -i '$a\ZABBIX_MYSQL_HOST=localhost' /etc/profile
sed -i '$a\ZABBIX_MYSQL_PORT=3306' /etc/profile
sed -i '$a\ZABBIX_MYSQL_BAK=/zabbix_backup' /etc/profile
sed -i '$a\ZABBIX_DATABASE=zabbix' /etc/profile
sed -i '$a\ZABBIX_LOGS=/tmp/zabbix.log' /etc/profile
source /etc/profile
if [[ $? -eq 0 ]]; then
echo "环境变量加载成功"
else
echo "环境变量加载失败"
exit 1
fi
}
prepare_dir(){
[ -d ${ZABBIX_MYSQL_BAK} ] || mkdir ${ZABBIX_MYSQL_BAK}
cd ${ZABBIX_MYSQL_BAK}
if [[ `pwd` = ${ZABBIX_MYSQL_BAK} ]]; then
echo "此时您的位置在${ZABBIX_MYSQL_BAK}"
else
echo "`pwd`"
exit 1
fi
#创建备份日志文件
if [[ -f $ZABBIX_LOGS ]]; then
echo "zabbix.log文件已经存在"
else
touch ${ZABBIX_LOGS}
fi
#创建数据库备份的目录
if [[ -d ${ZABBIX_MYSQL_BAK}/${DATE_DIR} ]]; then
echo "数据库备份的目录已经存在，无需再次创建"
else
mkdir ${ZABBIX_MYSQL_BAK}/${DATE_DIR}
fi
}
backup_table(){
ZABBIX_TABLE=`mysql -u${ZABBIX_MYSQL_USER} -p${ZABBIX_MYSQL_PASSWORD} -P${ZABBIX_MYSQL_PORT} -h${ZABBIX_MYSQL_HOST} ${ZABBIX_DATABASE} -e "show tables"`
for TABLE_NAME in ${ZABBIX_TABLE}
do
mysqldump -u${ZABBIX_MYSQL_USER} -p${ZABBIX_MYSQL_PASSWORD} -P${ZABBIX_MYSQL_PORT} ${ZABBIX_DATABASE} ${TABLE_NAME} > ${ZABBIX_MYSQL_BAK}/${DATE_DIR}/${TABLE_NAME}.sql
if [[ $? -eq 0 ]]; then
echo "${TABLE_NAME}表备份成功"
else
echo "${TABLE_NAME}表备份失败，请查看日志，分析原因，日志文件是${ZABBIX_LOGS}"
fi
done
}
package_dir(){
cd ${ZABBIX_MYSQL_BAK}
tar zcvf $DATE_DIR.tar.gz $DATE_DIR
if [[ $? -eq 0 && -f ${ZABBIX_MYSQL_BAK}/${DATE_DIR}.tar.gz ]];
then
echo "${DATE_DIR}的数据库备份文件已经成功打包"
else
exit 1
fi
}
clean_crash(){
rm -rf ${ZABBIX_LOGS}
rm -rf ${ZABBIX_MYSQL_BAK}/${DATE_DIR}
find ${ZABBIX_MYSQL_BAK} -type f -name "${DATE_DIR}.tar.gz" -atime +5 | xargs rm -rf
}
install_all(){
export DATE_DIR=`date -d '1 days ago' '+%Y%m%d'`
source /etc/profile
alls=(source_profile prepare_dir backup_table package_dir clean_crash)
for all in ${alls[*]};
do
if [[ $all = "source_profile" ]];
then
grep -q ZABBIX /etc/profile
if [[ $? -eq 0 ]]; then
continue;
else
${all}
fi
else
${all}
fi
done
}
main(){
install_all
echo "zabbix数据库备份成功，请查看"
}
main

```

###nginx.conf配置文件
```
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;
# Load dynamic modules. See /usr/share/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;
events {
worker_connections 1024;
}
http {
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
'$status $body_bytes_sent "$http_referer" '
'"$http_user_agent" "$http_x_forwarded_for"';
access_log /var/log/nginx/access.log main;
fastcgi_connect_timeout 60;
fastcgi_send_timeout 180;
fastcgi_read_timeout 180;
fastcgi_buffer_size 128k;
fastcgi_buffers 4 256k;
fastcgi_busy_buffers_size 256k;
fastcgi_temp_file_write_size 256k;
fastcgi_intercept_errors on;
sendfile on;
tcp_nopush on;
tcp_nodelay on;
keepalive_timeout 65;
types_hash_max_size 2048;
include /etc/nginx/mime.types;
default_type application/octet-stream;
# Load modular configuration files from the /etc/nginx/conf.d directory.
# See http://nginx.org/en/docs/ngx_core_module.html#include
# for more information.
include /etc/nginx/conf.d/*.conf;
server {
listen 80 default_server;
listen [::]:80 default_server;
server_name _;
root /usr/share/nginx/html;
# Load configuration files for the default server block.
include /etc/nginx/default.d/*.conf;
location / {
root /usr/share/nginx/html;
index index.php index.html index.htm; #增加index.php
}
location ~ \.php$ {
root /usr/share/nginx/html; #修改为nginx默认路径
fastcgi_pass 127.0.0.1:9000;
fastcgi_index index.php;
fastcgi_param SCRIPT_FILENAME /usr/share/nginx/html$fastcgi_script_name;
include fastcgi_params;
}
error_page 404 /404.html;
location = /40x.html {
}
error_page 500 502 503 504 /50x.html;
location = /50x.html {
}
}
}

```