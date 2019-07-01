export const TASK_TYPE = {
  INPUT: 1,
  CHECK: 2
}

export const TASKS = [
  {id: 1, text: '拉代码', type: TASK_TYPE.INPUT, param: 'version', place: 'Version'},
  {id: 2, text: '更改配置', type: TASK_TYPE.CHECK},
  {id: 3, text: '安装依赖', type: TASK_TYPE.CHECK},
  {id: 4, text: '重启服务', type: TASK_TYPE.CHECK},
  {id: 5, text: 'Django 脚本', type: TASK_TYPE.INPUT, once: true, param: 'command', place: ''},
  {id: 6, text: 'shell命令', type: TASK_TYPE.INPUT, param: 'raw'},
  {id: 7, text: 'Vue编译', type: TASK_TYPE.CHECK},
  {id: 12, text: '编译机部署环境', type: TASK_TYPE.CHECK},
  {id: 14, text: '编译机执行脚本', type: TASK_TYPE.INPUT, param: 'raw'},
  {id: 17, text: '部署静态文件', type: TASK_TYPE.CHECK}
]

export const PLAN_STATUS = {
  EDITING: 1,       // 正在编辑
  AUDIT_PASS: 3,    // 待上线
  GOLIVING: 4,      // 正在上线
  GOLIVED: 5,       // 已上线
  FAILED: 6         // 上线失败
}

export const GREY_STATUS = {
  NORMAL: 0,        // 正常
  PROCESSING: 1,    // 正在开始
  SUCCESS: 2,       // 执行成功
  FAIL: 3,          // 执行失败
  RESETTING: 4,     // 重置中
  RESET_FAIL: 5     // 重置失败
}

// 使用非service mesh形式的灰度的服务（暂时性，之后会完全下线老的灰度方式）
export const SERVICE_GREY_IN_OLD_WAY = [
  'flag-ship',
  'hera',
  'doris-admin',
  'kefu',
  'ship',
  'bran-collect',
  'mars',
  'gateway',
  'hermes',
  'ascle'
]
