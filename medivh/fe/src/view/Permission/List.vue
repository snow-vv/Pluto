<template>
  <div class="box box-primary">
    <div class="box-header with-border">
      <h3 class="box-title">权限列表</h3>
    </div>
    <table-box :url="url">
      <tr slot="ths">
        <th>ID</th>
        <th>Code</th>
        <th>描述</th>
      </tr>
      <template slot="item" scope="props">
        <tr>
          <td>
            {{ props.item.id }}
          </td>
          <td>
            {{ props.item.code }}
          </td>
          <td>
            {{ props.item.description }}
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
        url: API.list
      }
    }
  }
</script>
