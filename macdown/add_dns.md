##添加DNS解析脚本
```
#!/bin/bash
## add by zhaolei 20190427
HOSTNAME=$1
IP=$2
RevIP=`echo $IP | awk -F. '{print $4}'`
TIME=`date +%Y%m%d`
ParNum=$#
#ProdFile=/tmp/prod.gengmei.zone
#RevFile=/tmp/10.zone
ProdFile=/var/named/prod.alpha.zone
RevFile=/var/named/prod.alpha
ProdFileBak=${RevFile}.${TIME}.bak
ProdSerNumOld=`awk 'NR==3 {print $1}' $ProdFile`
#ProdSerNumNew=$(($ProdSerNumOld + 1))
ProdSerNumNew=`expr $ProdSerNumOld + 1`
RevFileBak=${ProdFile}.${TIME}.bak
RevSerNumOld=`awk 'NR==3 {print $1}' $RevFile`
RevSerNumNew=$(($RevSerNumOld + 1))
MakeSureAct () {
        echo "Usage: 如果添加gaia11主机的域名解析"
        echo " 请输入：$0 gaia11 10.31.51.226"
        echo " 请确认使用方式是否正确，确认请输入'Yes|yes'"
        echo " 错误请使用Ctrl+C中断操作"
        echo " 否则会导致DNS无法解析"
        read -p " please input Yes or No : " Cont
        if [ $Cont = Yes -o $Cont = yes -o $Cont = YES ];
           then
               if [ $ParNum = 2 ]
                  then
                     echo "继续执行。。。"
               else
                     echo "请依照Usage 确认参数是否正确 ？"
                     exit 1
               fi
        else
           echo "中断操作"
           exit 1
        fi
}

ChangeSerNum () {
         sed -i "3 s#$ProdSerNumOld#$ProdSerNumNew#g" $ProdFile
         sed -i "3 s#$RevSerNumOld#$RevSerNumNew#g" $RevFile
}

CheProdFile (){
         cp $ProdFile $ProdFileBak
         echo "$HOSTNAME IN A $IP" >> $ProdFile
}

CheRevFile (){
         cp $RevFile $RevFileBak
         echo "$RevIP PTR $HOSTNAME.prod.alpha." >> $RevFile
         sed -i "3 s#$RevSerNumOld#$RevSerNumNew#g" $RevFile
}

RollBack () {
         cp $ProdFileBak $ProdFile
         cp $RevFileBak $RevFile
         ProdSerNumNew=$(($ProdSerNumOld + 2))
         RevSerNumNew=$(($RevSerNumOld + 2))
         ChangeSerNum
         echo "rndc reload"
}

AndDnsRes () {
         grep "$HOSTNAME" $ProdFile
         if [ $? != 0 ]
            then
              CheProdFile
              CheRevFile
              ChangeSerNum
              systemctl restart named
         else
              echo "The hostname is already in the dns server ,please check it "
         fi
}
MakeSureAct
AndDnsRes
#sleep 5
#RollBack
```