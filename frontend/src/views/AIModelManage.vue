<template>
  <div class="page-container">
    <h2 class="page-title">AI模型管理</h2>

    <div class="content-card">
      <div class="toolbar">
        <span style="color: #909399">管理解析模型及API配置，用户可自由选择模型进行小说解析</span>
        <el-button type="primary" @click="openForm()">添加模型</el-button>
      </div>

      <el-table :data="models" v-loading="loading" stripe>
        <el-table-column prop="name" label="模型名称" width="150" />
        <el-table-column prop="provider" label="提供商" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.provider }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_identifier" label="模型标识" width="180" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="avg_speed" label="速度" width="80" />
        <el-table-column label="适配篇幅" width="120">
          <template #default="{ row }">
            {{ row.supported_max_chars ? formatCount(row.supported_max_chars) + '字' : '不限' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="handleTest(row)">测试</el-button>
            <el-button size="small" link @click="openForm(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 测试结果弹窗 -->
    <el-dialog v-model="testDialogVisible" title="模型连接测试" width="500px">
      <div v-loading="testing">
        <template v-if="testResult">
          <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? '连接成功' : '连接失败'"
          >
            <template #sub-title>
              <p v-if="testResult.success">
                响应时间: {{ testResult.response_time_ms?.toFixed(0) }}ms
              </p>
              <p v-if="testResult.response_text" style="margin-top: 8px; color: #606266">
                {{ testResult.response_text }}
              </p>
              <p v-if="testResult.error_message" style="color: #f56c6c">
                {{ testResult.error_message }}
              </p>
            </template>
          </el-result>
        </template>
      </div>
    </el-dialog>

    <!-- 添加/编辑模型弹窗 -->
    <ModelFormDialog
      v-model="showFormDialog"
      :model-data="editingModel"
      @saved="fetchModels"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getModels, deleteModel, testModel, updateModel } from '@/api/aiModel'
import ModelFormDialog from '@/components/ModelFormDialog.vue'

const models = ref([])
const loading = ref(false)
const showFormDialog = ref(false)
const editingModel = ref(null)
const testDialogVisible = ref(false)
const testing = ref(false)
const testResult = ref(null)

async function fetchModels() {
  loading.value = true
  try {
    const data = await getModels()
    models.value = data.items || data
  } catch { /* handled */ } finally {
    loading.value = false
  }
}

function openForm(model = null) {
  editingModel.value = model
  showFormDialog.value = true
}

async function toggleActive(row) {
  try {
    await updateModel(row.id, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已停用')
  } catch {
    row.is_active = !row.is_active
  }
}

async function handleTest(row) {
  testDialogVisible.value = true
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await testModel(row.id, { test_prompt: '你好，请简单回复。' })
  } catch {
    testResult.value = { success: false, error_message: '测试请求失败' }
  } finally {
    testing.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除模型「${row.name}」？`, '确认', { type: 'warning' })
  await deleteModel(row.id)
  ElMessage.success('删除成功')
  fetchModels()
}

function formatCount(n) {
  if (!n) return '0'
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toString()
}

onMounted(fetchModels)
</script>
