<script setup name="home">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import OAMain from "@/components/OAMain.vue"
import homeHttp from "@/api/homeHttp"
import * as echarts from "echarts"

let informs = ref([])
let absents = ref([])

onMounted(async () => {
  try {
    // 获取最新通知 & 请假
    const informs_data = await homeHttp.getLatestInforms()
    const absents_data = await homeHttp.getLatestAbsents()
    informs.value = informs_data.data.data
    absents.value = absents_data.data.data

    // 获取部门员工数量
    const { data } = await homeHttp.getDepartmentStaffCount()
    const staffList = data.data

    const xdatas = staffList.map(row => row.name)
    const ydatas = staffList.map(row => row.staff_count)

    // 初始化图表
    const myChart = echarts.init(document.getElementById("department-staff-count"))
    myChart.setOption({
      tooltip: {
        trigger: "axis",
        formatter: "{b}：{c} 人"
      },
      grid: { left: "5%", right: "5%", bottom: "10%", containLabel: true },
      xAxis: {
        type: "category",
        data: xdatas,
        axisLine: { lineStyle: { color: "#ddd" } },
        axisLabel: { color: "#666" }
      },
      yAxis: {
        type: "value",
        axisLine: { show: false },
        splitLine: { lineStyle: { color: "#eee" } },
        axisLabel: { color: "#666" }
      },
      series: [
        {
          name: "员工数量",
          type: "bar",
          data: ydatas,
          barWidth: "40%",
          itemStyle: {
            borderRadius: [6, 6, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#409EFF" },
              { offset: 1, color: "#67C23A" }
            ])
          }
        }
      ]
    })

    // 监听窗口大小变化，调整图表尺寸
    window.addEventListener('resize', () => {
      myChart.resize();
    });
  } catch (err) {
    console.log(err)
    ElMessage.error(err.msg || "加载数据失败")
  }
})
</script>

<template>
  <OAMain title="首页" class="main-container">
    <!-- 部门员工数量 -->
    <el-card class="dashboard-card">
      <template #header>
        <h2>部门员工数量</h2>
      </template>
      <div id="department-staff-count" class="chart-container"></div>
    </el-card>

    <!-- 通知 & 请假 -->
    <el-row :gutter="20" class="table-row">
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <h2>最新通知</h2>
          </template>
          <el-table :data="informs" class="info-table">
            <el-table-column label="标题">
              <template #default="scope">
                <router-link
                  :to="{ name: 'informdetail', params: { inform_id: scope.row.id } }"
                  class="table-link"
                  >{{ scope.row.title }}</router-link
                >
              </template>
            </el-table-column>
            <el-table-column label="发布者" prop="author_name"></el-table-column>
            <el-table-column label="发布时间">
              <template #default="scope">
                <span class="time-text">{{ scope.row.create_time }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <h2>最近请假</h2>
          </template>
          <el-table :data="absents" class="info-table">
            <el-table-column label="发起人" prop="requester_name"></el-table-column>
            <el-table-column label="起始日期" prop="start_date"></el-table-column>
            <el-table-column label="结束日期" prop="end_date"></el-table-column>
            <el-table-column label="发起时间">
              <template #default="scope">
                <span class="time-text">{{ scope.row.create_time }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </OAMain>
</template>

<style scoped>
/* 主容器样式，防止溢出 */
.main-container {
  padding: 16px;
  box-sizing: border-box;
  max-width: 100vw;
  overflow-x: hidden;
}

/* 卡片样式优化 */
.dashboard-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease-in-out;
  margin-bottom: 16px;
}
.dashboard-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

/* 标题样式 */
.dashboard-card h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-left: 4px solid #409EFF;
  padding-left: 8px;
  margin: 0;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 280px; /* 略微减小图表高度 */
  box-sizing: border-box;
}

/* 表格行间距 */
.table-row {
  margin-top: 16px !important;
}

/* 表格优化 */
.info-table {
  font-size: 14px;
  height: 260px; /* 减小表格高度 */
  box-sizing: border-box;
}
.el-table tr:hover {
  background-color: #f9fafc;
}
.table-link {
  color: #409EFF;
  font-weight: 500;
  text-decoration: none;
}
.table-link:hover {
  text-decoration: underline;
}
.time-text {
  color: #999;
  font-size: 13px;
}

/* 确保表格内容不溢出 */
.el-table__cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
