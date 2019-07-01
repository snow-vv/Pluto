npm run build
scp -r dist/static/* root@system.env:/srv/static/medivh/
scp dist/index.html root@system.env:/srv/apps/medivh/templates/index.html
