# README #

### install

0. node version >= 4.x
1. nvm https://www.jianshu.com/p/20ea93641bda `nvm install 6.9.1`
2. cd fe && npm install && npm run build


### deploy to prod

cd fe && sh prod.sh


### 灰度控制

1. 选择要灰度的服务，点击执行，会弹窗显示将要执行的步骤，确认没问题后，点击confirm执行灰度
2. 灰度确认新版本没问题后，更新线上服务
3. 完成线上服务的更新后，执行重置命令，会弹窗提示要执行的步骤，确认OK后，点击confirm执行重置

