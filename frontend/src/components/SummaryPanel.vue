<template>
  <div class="content-card">
    <h3 style="margin-bottom: 12px">内容总结</h3>

    <!-- 生成控制 -->
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap">
      <span style="color: #909399; white-space: nowrap">总结长度：</span>
      <el-slider v-model="targetLength" :min="50" :max="300" :step="10" style="flex: 1; min-width: 200px" show-input />
      <el-select v-model="selectedModelId" placeholder="选择AI模型" style="width: 200px" clearable>
        <el-option v-for="m in aiModels" :key="m.id" :label="m.name" :value="m.id" />
      </el-select>
      <el-button type="primary" @click="handleGenerate" :loading="generating">
        生成总结
      </el-button>
    </div>

    <!-- 总结内容展示 -->
    <div v-if="currentSummary">
      <div v-if="!editing" style="line-height: 1.8; color: #303133; padding: 12px; background: #fafafa; border-radius: 6px">
        {{ currentSummary.content }}
        <div style="margin-top: 8px; color: #c0c4cc; font-size: 12px">
          字数：{{ currentSummary.actual_length }} | 模型：{{ currentSummary.model_used || '默认' }}
        </div>
      </div>
      <div v-else>
        <el-input v-model="editContent" type="textarea" :rows="6" />
      </div>
      <div style="margin-top: 8px">
        <template v-if="!editing">
          <el-button size="small" @click="startEdit">编辑</el-button>
        </template>
        <template v-else>
          <el-button size="small" type="primary" @click="saveEdit" :loading="savingEdit">保存</el-button>
          <el-button size="small" @click="editing = false">取消</el-button>
        </template>
      </div>
    </div>

    <el-empty v-else-if="!generating" description="暂无总结，请点击「生成总结」" />

    <!-- 历史总结列表 -->
    <div v-if="summaries.length > 1" style="margin-top: 16px">
      <el-collapse>
        <el-collapse-item title="历史总结记录">
          <div v-for="s in summaries" :key="s.id" style="margin-bottom: 12px; padding: 8px; background: #fafafa; border-radius: 4px">
            <p>{{ s.content }}</p>
            <p style="color: #c0c4cc; font-size: 12px; margin-top: 4px">
              {{ new Date(s.created_at).toLocaleString('zh-CN') }} | {{ s.actual_length }}字 | {{ s.model_used || '默认' }}
            </p>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { generateSummary, updateSummary } from '@/api/summary'
import { getModels } from '@/api/aiModel'

const props = defineProps({
  novelId: { type: [Number, String], required: true },
  summaries: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh'])

const targetLength = ref(100)
const selectedModelId = ref(null)
const generating = ref(false)
const editing = ref(false)
const editContent = ref('')
const savingEdit = ref(false)
const aiModels = ref([])

const currentSummary = computed(() => {
  // 获取最新的非分段总结（列表已按 created_at 降序排列，第一个即最新）
  const full = props.summaries.filter(s => !s.is_chunk_summary)
  return full.length > 0 ? full[0] : null
})

async function handleGenerate() {
  generating.value = true
  try {
    await generateSummary(props.novelId, {
      target_length: targetLength.value,
      model_id: selectedModelId.value
    })
    ElMessage.success('总结生成完成')
    emit('refresh')
  } catch { /* handled */ } finally {
    generating.value = false
  }
}

function startEdit() {
  editContent.value = currentSummary.value.content
  editing.value = true
}

async function saveEdit() {
  savingEdit.value = true
  try {
    await updateSummary(currentSummary.value.id, { content: editContent.value })
    ElMessage.success('保存成功')
    editing.value = false
    emit('refresh')
  } catch { /* handled */ } finally {
    savingEdit.value = false
  }
}

onMounted(async () => {
  try {
    const data = await getModels({ active_only: true })
    aiModels.value = data.items || data
  } catch { /* handled */ }
})
</script>
