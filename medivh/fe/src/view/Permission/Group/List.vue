<template>
  <div class="box box-primary">
    <div class="box-header with-border">
      <h3 class="box-title">权限组列表</h3>
      <div class="box-tools">
        <router-link class="btn btn-block btn-primary btn-sm" :to="{ name: 'permission_group_new'}">
          新权限组
        </router-link>
      </div>
    </div>
    <table-box :url="url">
      <tr slot="ths">
        <th>ID</th>
        <th>名称</th>
        <th>用户</th>
        <th>权限</th>
        <th>操作</th>
      </tr>
      <template slot="item" scope="props">
        <tr>
          <td>
            {{ props.item.id }}
          </td>
          <td>
            {{ props.item.name }}
          </td>
          <td>
            <ul v-if="props.item.users.length">
              <li v-for="user in props.item.users">{{ user.name }}</li>
            </ul>
          </td>
          <td>
            <ul v-if="props.item.permissions.length">
              <li v-for="permission in props.item.permissions">{{ permission.code }}</li>
            </ul>
          </td>
          <td>
            <button type="button" class="btn btn-info" @click="goEdit(props.item.id)">
              编辑
            </button>
          </td>
        </tr>
      </template>
    </table-box>
  </div>
</template>

<script>
  import { permission as API } from '@/constants/api'
  import TableBox from '@/components/global/TableBox'

  export default {
    components: {TableBox},

    data () {
      return {
        url: API.groups
      }
    },

    methods: {

      goEdit (id) {
        this.$router.push({name: 'permission_group_edit', params: {id: id}})
      }

    }
  }
</script>
