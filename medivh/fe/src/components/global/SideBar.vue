<template>
  <aside class="main-sidebar">
    <section class="sidebar" style="height: 600px; overflow: hidden; width: auto;">
      <UserPanel></UserPanel>
      <SideBarItem :data="navs"></SideBarItem>
      <OutLinkSideBarItem :data="out_navs"></OutLinkSideBarItem>
    </section>
  </aside>
</template>

<script>
  import UserPanel from '@/components/global/UserPanel'
  import SideBarItem from '@/components/global/SideBarItem'
  import OutLinkSideBarItem from '@/components/global/OutLinkSideBarItem'

  export default {
    components: {UserPanel, SideBarItem, OutLinkSideBarItem},

    data () {
      return {
        navs: [
          {
            name: '上线申请',
            to: 'plan_list',
            paths: ['plan'],
            icon: 'fa-dashboard'
          },
          {
            name: '服务列表',
            to: 'service_list',
            paths: ['service'],
            icon: 'fa-cloud'
          },
          {
            name: 'ECS列表',
            to: 'ecs_list',
            paths: ['ecs'],
            icon: 'fa-server'
          },
          {
            name: '灰度控制',
            to: 'grey_list',
            paths: ['grey'],
            icon: 'fa-hourglass-3'
          },
          {
            name: 'Service Mesh灰度控制',
            to: 'mesh_grey_list',
            paths: ['mesh_greys'],
            icon: 'fa-hourglass-2'
          },
          {
            name: 'GM-Shield黑名单',
            to: 'blackip_list',
            paths: ['shield'],
            icon: 'fa-shield'
          },
          {
            name: '服务关系图',
            to: 'graph',
            paths: ['graph'],
            icon: 'fa-connectdevelop'
          },
          {
            name: '权限',
            paths: ['permissions'],
            to: '#',
            icon: 'fa-lock',
            subNavs: [{
              name: '权限列表',
              to: 'permission_list',
              paths: ['permissions'],
              icon: 'fa-circle-o'
            }, {
              name: '权限组',
              to: 'permission_group_list',
              paths: ['permission/groups'],
              icon: 'fa-circle-o'
            }]
          },
          {
            name: '审计',
            paths: ['audit'],
            to: '#',
            icon: 'fa-calendar-minus-o',
            subNavs: [{
              name: '执行记录',
              to: 'audit_executions',
              paths: ['audit/executions'],
              icon: 'fa-circle-o'
            }]
          }
        ],
        out_navs: [
          {
            name: '监控',
            paths: [],
            to: '#',
            icon: 'fa-line-chart',
            subNavs: [{
              name: 'Sentry',
              to: 'http://sentry.igengmei.com/auth/login/sentry/',
              paths: [],
              icon: 'fa-circle-o'
            }, {
              name: 'Grafana',
              to: 'http://monitor.igengmei.com/',
              paths: [],
              icon: 'fa-circle-o'
            }, {
              name: 'argus',
              to: 'http://argus.wanmeizhensuo.com/login',
              paths: [],
              icon: 'fa-circle-o'
            }, {
              name: 'zipkin',
              to: 'http://medivh.prod.gengmei/zipkin/',
              paths: [],
              icon: 'fa-circle-o'
            }]
          }
        ]
      }
    }
  }
</script>
