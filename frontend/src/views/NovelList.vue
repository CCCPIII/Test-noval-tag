<template>
  <div class="page-container">
    <h2 class="page-title">小说列表</h2>

    <div class="toolbar">
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px" @change="fetchList">
        <el-option label="全部" value="" />
        <el-option label="已上传" value="uploaded" />
        <el-option label="处理中" value="processing" />
        <el-option label="已完成" value="done" />
        <el-option label="出错" value="error" />
      </el-select>
      <el-button type="primary" @click="$router.push('/upload')">
        <el-icon><Upload /></el-icon> 上传小说
      </el-button>
    </div>

    <div class="content-card">
      <el-table :data="novels" v-loading="loading" stripe @row-click="goDetail">
        <el-table-column prop="title" label="书名" min-width="200" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column label="字数" width="120">
          <template #default="{ row }">
            {{ formatCharCount(row.char_count) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.upload_time).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click.stop="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; text-align: right">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchList"
          @size-change="fetchList"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getNovelList, deleteNovel } from '@/api/novel'

const router = useRouter()
const novels = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const loading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const data = await getNovelList({
      page: page.value,
      page_size: pageSize.value,
      status: statusFilter.value || undefined
    })
    novels.value = data.items
    total.value = data.total
  } catch { /* handled */ } finally {
    loading.value = false
  }
}

function goDetail(row) {
  router.push(`/novel/${row.id}`)
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除《${row.title}》及其所有总结和标签？`, '确认删除', { type: 'warning' })
  await deleteNovel(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

function formatCharCount(count) {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toString()
}

function statusType(status) {
  const map = { uploaded: 'info', processing: 'warning', done: 'success', error: 'danger' }
  return map[status] || 'info'
}

function statusLabel(status) {
  const map = { uploaded: '已上传', processing: '处理中', done: '已完成', error: '出错' }
  return map[status] || status
}

onMounted(fetchList)
</script>
