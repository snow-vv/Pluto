<template>
  <div class="box box-primary">
    <div class="box-header with-border">
      <h3 class="box-title">执行记录</h3>
    </div>
    <table-box :url="url">
      <tr slot="ths">
        <th>ID</th>
        <th>执行人</th>
        <th>执行目标</th>
        <th>开始时间</th>
        <th>结束时间</th>
      </tr>
      <template slot="item" scope="props">
        <tr>
          <td>
            {{ props.item.id }}
          </td>
          <td>
            {{ props.item.user.name }}
          </td>
          <td>
            {{ props.item.target }}
          </td>
          <td>
            {{ props.item.start_time | date(true) }}
          </td>
          <td>
            {{ props.item.end_time | date(true) }}
          </td>
        </tr>
      </template>
    </table-box>
  </div>
</template>

<script>
  import {audit as API} from '@/constants/api'
  import TableBox from '@/components/global/TableBox'

  export default {
    components: {TableBox},
    data () {
      return {
        url: API.executions
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
