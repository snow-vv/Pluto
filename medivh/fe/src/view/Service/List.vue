<template>
  <div class="box box-primary">
    <div class="box-header with-border">
      <h3 class="box-title">服务列表</h3>
    </div>
    <table-box :url="url">
      <tr slot="ths">
        <th>ID</th>
        <th>名称</th>
        <th>Git地址</th>
        <th>ECS列表</th>
        <th>SLB</th>
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
            {{ props.item.git_repo }}
          </td>
          <td>
            <ul v-if="props.item.ecses.length">
              <li v-for="ecs in props.item.ecses">{{ ecs.name }}</li>
            </ul>
          </td>
          <td>
            <ul v-if="props.item.slbs.length">
              <li v-for="slb in props.item.slbs">
                <router-link :to="{name: 'slb_detail', params:{'id': slb.id}}">{{ slb.name }}</router-link>
              </li>
            </ul>
          </td>
        </tr>
      </template>
    </table-box>
  </div>
</template>

<script>
  import { cmdb as API } from '@/constants/api'
  import TableBox from '@/components/global/TableBox'

  export default {
    components: {TableBox},

    data () {
      return {
        url: API.services
      }
    },

    methods: {}
  }
</script>
