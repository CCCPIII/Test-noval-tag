<template>
  <div class="page-container">
    <h2 class="page-title">AI模型管理</h2>

    <!-- 配置指南 -->
    <el-collapse v-model="guideOpen" style="margin-bottom: 20px">
      <el-collapse-item name="guide">
        <template #title>
          <el-icon style="margin-right: 6px"><InfoFilled /></el-icon>
          <strong>模型配置指南</strong>
          <el-tag size="small" type="info" style="margin-left: 8px">点击展开查看支持的模型和配置方式</el-tag>
        </template>
        <div class="guide-content">
          <p style="margin-bottom: 12px; color: #606266">
            系统支持主流 AI 模型，添加模型时选择对应的<strong>提供商</strong>，填入 API 地址、密钥和模型标识即可。
            大部分国产模型都兼容 OpenAI 格式，提供商选 <el-tag size="small">OpenAI / 兼容格式</el-tag> 即可。
          </p>
          <el-table :data="guideData" stripe size="small" :show-header="true" style="width: 100%">
            <el-table-column prop="name" label="模型" width="120" />
            <el-table-column prop="provider" label="提供商选择" width="160">
              <template #default="{ row }">
                <el-tag size="small" :type="row.providerType || ''">{{ row.provider }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="apiUrl" label="API 地址" min-width="280">
              <template #default="{ row }">
                <code style="font-size: 12px; color: #409eff; word-break: break-all">{{ row.apiUrl }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="modelId" label="模型标识示例" width="180">
              <template #default="{ row }">
                <code style="font-size: 12px">{{ row.modelId }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="keySource" label="密钥获取" width="160">
              <template #default="{ row }">
                <span style="font-size: 12px; color: #909399">{{ row.keySource }}</span>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 12px; padding: 10px; background: #f5f7fa; border-radius: 4px; font-size: 13px; color: #606266">
            <p><strong>提示：</strong></p>
            <ul style="margin: 4px 0 0 16px; line-height: 1.8">
              <li>API 地址填到 <code>/v1</code> 即可，系统会自动补全完整路径</li>
              <li>添加后点击「测试」按钮验证连接是否正常</li>
              <li>可同时添加多个模型，在生成总结/标签时选择使用哪个</li>
              <li>如果模型不在上表中，但兼容 OpenAI 格式，提供商选「OpenAI / 兼容格式」即可</li>
            </ul>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

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
import { InfoFilled } from '@element-plus/icons-vue'
import { getModels, deleteModel, testModel, updateModel } from '@/api/aiModel'
import ModelFormDialog from '@/components/ModelFormDialog.vue'

const guideOpen = ref([])
const guideData = [
  { name: 'DeepSeek', provider: 'OpenAI / 兼容格式', providerType: '', apiUrl: 'https://api.deepseek.com/v1', modelId: 'deepseek-chat', keySource: 'platform.deepseek.com' },
  { name: '通义千问', provider: 'OpenAI / 兼容格式', providerType: '', apiUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', modelId: 'qwen-turbo / qwen-plus', keySource: 'dashscope.console.aliyun.com' },
  { name: '豆包', provider: 'OpenAI / 兼容格式', providerType: '', apiUrl: 'https://ark.cn-beijing.volces.com/api/v3', modelId: '你的模型端点 ID', keySource: 'console.volcengine.com' },
  { name: '月之暗面 Kimi', provider: 'OpenAI / 兼容格式', providerType: '', apiUrl: 'https://api.moonshot.cn/v1', modelId: 'moonshot-v1-8k', keySource: 'platform.moonshot.cn' },
  { name: '零一万物', provider: 'OpenAI / 兼容格式', providerType: '', apiUrl: 'https://api.lingyiwanwu.com/v1', modelId: 'yi-large', keySource: 'platform.01.ai' },
  { name: 'OpenAI', provider: 'OpenAI / 兼容格式', providerType: '', apiUrl: 'https://api.openai.com/v1', modelId: 'gpt-4o-mini', keySource: 'platform.openai.com' },
  { name: 'Claude', provider: 'Anthropic Claude', providerType: 'warning', apiUrl: 'https://api.anthropic.com/v1', modelId: 'claude-sonnet-4-20250514', keySource: 'console.anthropic.com' },
  { name: 'Gemini', provider: 'Google Gemini', providerType: 'success', apiUrl: '留空使用默认地址', modelId: 'gemini-2.0-flash', keySource: 'aistudio.google.com' },
  { name: '智谱 ChatGLM', provider: '智谱AI', providerType: 'danger', apiUrl: '留空使用默认地址', modelId: 'glm-4', keySource: 'open.bigmodel.cn' },
]

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
