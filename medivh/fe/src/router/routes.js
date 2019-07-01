import { login, exec } from './guards.js'

import Login from '@/view/Account/Login'
import Psw from '@/view/Account/Psw'
import Layout from '@/view/Layout'

import Plan from '@/view/Plan/Plan'
import PlanList from '@/view/Plan/List'
import Execution from '@/view/Execution/Execution'
import Host from '@/view/Execution/Host'

import ServiceList from '@/view/Service/List'
import SLBDetail from '@/view/Service/SLBDetail'
import GreyList from '@/view/Grey/List'
import MeshGreyList from '@/view/MeshGrey/List'
import EcsList from '@/view/Ecs/List'
import BlackIpList from '@/view/Shield/List'

import Graph from '@/view/Graph/Graph'

import PermissionList from '@/view/Permission/List'
import PermissionGroupList from '@/view/Permission/Group/List'
import PermissionGroupEdit from '@/view/Permission/Group/Edit'
import PermissionGroupNew from '@/view/Permission/Group/New'

import Executions from '@/view/Audit/Executions'

export default [
  {path: '/login', name: 'login', component: Login},

  {
    path: '/',
    name: 'root',
    component: Layout,
    redirect: '/plans',
    beforeEnter: login,

    children: [
      {path: '/password', name: 'password', component: Psw},
      {path: '/plans', name: 'plan_list', component: PlanList, meta: {contentHeader: {title: '上线申请'}}},
      {path: '/plans/new', name: 'plan_new', component: Plan, meta: {contentHeader: {title: '创建申请'}}},
      {path: '/plans/:id', name: 'plan_edit', component: Plan, meta: {contentHeader: {title: '申请详情'}}},
      {
        path: '/executions/:id',
        name: 'execution',
        component: Execution,
        meta: {contentHeader: {title: '执行详情'}}
      },
      {
        path: '/executions/stage/:stageId/host/:hostId',
        name: 'executionHost',
        component: Host,
        meta: {contentHeader: {title: '上线步骤'}}
      },

      {path: '/services', name: 'service_list', component: ServiceList, meta: {contentHeader: {title: '服务列表'}}},
      {path: '/services/slbs/:id', name: 'slb_detail', component: SLBDetail, meta: {contentHeader: {title: 'SLB详情'}}},

      {path: '/greys', name: 'grey_list', component: GreyList, meta: {contentHeader: {title: '灰度控制'}}},

      {path: '/mesh_greys', name: 'mesh_grey_list', component: MeshGreyList, meta: {contentHeader: {title: 'Service Mesh 灰度控制'}}},

      {path: '/ecses', name: 'ecs_list', component: EcsList, meta: {contentHeader: {title: 'ECS列表'}}},

      {
        path: '/shield/blackips',
        name: 'blackip_list',
        component: BlackIpList,
        meta: {contentHeader: {title: '黑名单', subTitle: 'gm-shield'}}
      },

      {path: '/graph', name: 'graph', component: Graph, meta: {contentHeader: {title: '服务关系图'}}},

      {
        path: '/permissions',
        name: 'permission_list',
        component: PermissionList,
        meta: {contentHeader: {title: '权限列表'}}
      },
      {
        path: '/permission/groups',
        name: 'permission_group_list',
        component: PermissionGroupList,
        meta: {contentHeader: {title: '权限组'}}
      },
      {
        path: '/permission/groups/:id/edit',
        name: 'permission_group_edit',
        component: PermissionGroupEdit,
        meta: {contentHeader: {title: '编辑权限组'}}
      },
      {
        path: '/permission/groups/new',
        name: 'permission_group_new',
        component: PermissionGroupNew,
        meta: {contentHeader: {title: '新增权限组'}}
      },

      {
        path: '/audit/executions',
        name: 'audit_executions',
        component: Executions,
        meta: {contentHeader: {title: '操作记录'}}
      }
    ]
  },

  {path: '*', redirect: '/'}
]
