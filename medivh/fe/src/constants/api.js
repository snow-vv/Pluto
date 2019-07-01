/**
 * Created by Thierry on 2017/4/14.
 */

// golive
export const golive = {
  plans: '/golive/plans',
  plan: '/golive/plans/:id',
  commit: '/golive/service/commits',
  createPlan: '/golive/plans/create',
  services: '/golive/services',

  grey_services: '/golive/grey_services',
  execPlan: '/golive/plans/:id/executions',
  stageRollback: '/golive/stages/:id/rollback',
  stageHosts: '/golive/stages/:id/hosts',
  run: '/golive/stages/:stageId/run/:execId',
  runAll: '/golive/plans/:planId/run/:type',
  execResult: '/golive/executions/:id',
  hostExecResult: '/golive/stages/:stageId/hosts/:hostId/executions',
  releaseDone: '/golive/plans/:planId/done',

  greys: '/golive/greys',
  confirmGrey: '/golive/greys/:id/confirm',
  confirmReset: '/golive/greys/:id/confirm_reset',
  greyStart: '/golive/greys/:id/start',
  greyReset: '/golive/greys/:id/reset',

  greyRule: '/golive/grey_rule',
  dtabRulesExample: '/golive/dtabrules_example'
}

// accounts
export const accounts = {
  login: '/accounts/login',
  logout: '/accounts/logout',
  psw: '/accounts/change_password'
}

// cmdb
export const cmdb = {
  services: '/cmdb/services',
  slb: '/cmdb/slbs/:id',
  slbChangeWeight: '/cmdb/slbs/:id/ecses/:ecsId/change_weight',
  ecses: '/cmdb/ecses',
  ecsesSync: '/cmdb/ecses/sync',
  users: '/cmdb/users'
}

// shield
export const shield = {
  blackips: '/shield/blackips',
  ipAdd: '/shield/:ip/add',
  ipDel: '/shield/:ip/del'
}

export const graph = {
  service: '/service/relation'
}

// 权限
export const permission = {
  list: '/permission/list',
  groups: '/permission/groups',
  group: '/permission/groups/:id',
  newGroup: '/permission/groups/create'
}

// 审计
export const audit = {
  executions: '/audit/executions'
}
