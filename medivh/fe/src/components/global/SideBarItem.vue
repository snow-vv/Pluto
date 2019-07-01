<template>
  <ul class="sidebar-menu">
    <li class="header" v-if="$route.path.includes('/projects')">
      <router-link :to="{ name: 'dashboard'}">
        Go to Dashboard
      </router-link>
    </li>
    <li class="header" v-else>
      MAIN NAVIGATION
    </li>
    <li class="treeview" :class="navCls(nav)" v-for="nav in navs">
      <a href="#" v-if="hasSubNavs(nav)">
        <i class="fa" :class="nav.icon"></i>
        <span>{{ nav.name }}</span>
        <span class="pull-right-container"><i class="fa fa-angle-left pull-right"></i></span>
      </a>
      <router-link :to="{name: nav.to}" v-else>
        <i class="fa" :class="nav.icon"></i>
        <span>{{ nav.name }}</span>
      </router-link>
      <ul class="treeview-menu" v-if="hasSubNavs(nav)">
        <li v-for="subNav in nav.subNavs" :class="navCls(subNav)">
          <router-link :to="{name: subNav.to}">
            <i class="fa" :class="subNav.icon"></i>
            <span>{{ subNav.name }}</span>
          </router-link>
        </li>
      </ul>
    </li>
  </ul>
</template>

<script>
  export default {
    props: ['data'],
    data () {
      return {
        navs: this.data
      }
    },

    methods: {

      navCls (nav) {
        let active = false
        for (let path of nav.paths) {
          if (this.$route.path.includes(path)) {
            active = true
          }
        }
        if (active) {
          return 'active'
        } else {
          return ''
        }
      },

      hasSubNavs (nav) {
        return nav.subNavs && nav.subNavs.length > 0
      }
    }
  }
</script>
