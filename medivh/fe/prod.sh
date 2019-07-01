npm run build
scp -r dist/static/* root@bastion.prod.gengmei:/srv/static/medivh/
scp dist/index.html root@bastion.prod.gengmei:/srv/apps/medivh/templates/index.html
