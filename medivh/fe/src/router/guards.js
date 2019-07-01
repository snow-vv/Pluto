import store from '@/store'

export function login(to, from, next) {
  let user = store.getters.currentUser
  if (user === null || user.id === null) {
    next({name: 'login'})
  } else {
    next()
  }
}

export function exec(to, from, next) {
  if (store.getters.currentUser.is_superuser) {
    next()
  } else {
    next({name: 'plan_list'})
  }
}
