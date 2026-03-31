<template>
  <div>
    <h4 style="margin-bottom: 8px; color: #606266">手动添加标签</h4>

    <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center">
      <!-- 从标签库选择 -->
      <el-select v-model="selectedLibraryTag" filterable placeholder="从标签库选择..." style="width: 200px">
        <el-option-group v-for="(tags, dim) in groupedTags" :key="dim" :label="dimensionLabel(dim)">
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="`${dim}:${t.name}`" />
        </el-option-group>
      </el-select>
      <el-button size="small" @click="addFromLibrary" :disabled="!selectedLibraryTag">添加</el-button>

      <el-divider direction="vertical" />

      <!-- 自定义标签输入 -->
      <el-input v-model="customTagName" placeholder="输入自定义标签" style="width: 150px" @keyup.enter="addCustomTag" />
      <el-select v-model="customDimension" style="width: 100px">
        <el-option label="题材" value="genre" />
        <el-option label="风格" value="style" />
        <el-option label="元素" value="element" />
        <el-option label="人物" value="character" />
      </el-select>
      <el-button size="small" @click="addCustomTag" :disabled="!customTagName">添加自定义</el-button>
    </div>

    <!-- 已有标签管理（删除、设置争议） -->
    <div v-if="existingTags.length > 0" style="margin-top: 12px">
      <div v-for="tag in existingTags" :key="tag.tag_id" style="display: inline-flex; align-items: center; margin: 4px 8px 4px 0">
        <el-tag :class="'tag-' + tag.dimension" closable @close="handleRemove(tag)">
          {{ tag.tag_name }}
        </el-tag>
        <el-checkbox
          v-model="tag.is_controversial"
          size="small"
          style="margin-left: 4px"
          @change="toggleControversy(tag)"
        >
          争议
        </el-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assignTag, removeTag, updateControversy } from '@/api/tag'
import { useTagLibraryStore } from '@/stores/tagLibrary'

const props = defineProps({
  novelId: { type: [Number, String], required: true },
  existingTags: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh'])
const tagStore = useTagLibraryStore()

const groupedTags = ref({})
const selectedLibraryTag = ref('')
const customTagName = ref('')
const customDimension = ref('genre')

async function addFromLibrary() {
  if (!selectedLibraryTag.value) return
  const [dimension, name] = selectedLibraryTag.value.split(':')
  try {
    await assignTag(props.novelId, { tag_name: name, dimension, is_manual: true })
    ElMessage.success('标签添加成功')
    selectedLibraryTag.value = ''
    emit('refresh')
  } catch { /* handled */ }
}

async function addCustomTag() {
  if (!customTagName.value) return
  try {
    await assignTag(props.novelId, {
      tag_name: customTagName.value,
      dimension: customDimension.value,
      is_manual: true,
      is_custom: true
    })
    ElMessage.success('自定义标签添加成功')
    customTagName.value = ''
    emit('refresh')
  } catch { /* handled */ }
}

async function handleRemove(tag) {
  await ElMessageBox.confirm(`确定移除标签「${tag.tag_name}」？`, '确认')
  await removeTag(props.novelId, tag.tag_id)
  ElMessage.success('标签已移除')
  emit('refresh')
}

async function toggleControversy(tag) {
  const note = tag.is_controversial
    ? await ElMessageBox.prompt('请输入争议说明（50字以内）', '争议标签', { inputPattern: /.{1,50}/, inputErrorMessage: '请输入1-50字的说明' }).then(r => r.value).catch(() => null)
    : ''
  if (tag.is_controversial && !note) {
    tag.is_controversial = false
    return
  }
  await updateControversy(props.novelId, tag.tag_id, {
    is_controversial: tag.is_controversial,
    controversy_note: note || ''
  })
  ElMessage.success('更新成功')
  emit('refresh')
}

function dimensionLabel(dim) {
  const map = { genre: '题材', style: '风格', element: '核心元素', character: '人物类型' }
  return map[dim] || dim
}

onMounted(async () => {
  await tagStore.fetchGroupedTags()
  groupedTags.value = tagStore.groupedTags
})
</script>
