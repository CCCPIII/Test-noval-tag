<template>
  <div class="page-container">
    <h2 class="page-title">标签库管理</h2>

    <div class="content-card">
      <el-tabs v-model="activeDimension" @tab-change="fetchTags">
        <el-tab-pane v-for="dim in dimensions" :key="dim.value" :label="dim.label" :name="dim.value" />
      </el-tabs>

      <div class="toolbar">
        <el-button type="primary" size="small" @click="showAddDialog = true">添加标签</el-button>
        <el-button size="small" @click="showBatchDialog = true">批量添加</el-button>
      </div>

      <el-table :data="tags" v-loading="loading" stripe>
        <el-table-column prop="name" label="标签名称" width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" link @click="editTag(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑标签弹窗 -->
    <el-dialog v-model="showAddDialog" :title="editingTag ? '编辑标签' : '添加标签'" width="450px">
      <el-form :model="tagForm" label-width="80px">
        <el-form-item label="标签名称" required>
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="tagForm.description" type="textarea" :rows="3" placeholder="标签描述（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="tagForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量添加弹窗 -->
    <el-dialog v-model="showBatchDialog" title="批量添加标签" width="500px">
      <p style="margin-bottom: 12px; color: #909399">每行输入一个标签名称：</p>
      <el-input v-model="batchText" type="textarea" :rows="10" placeholder="言情&#10;悬疑&#10;科幻&#10;..." />
      <template #footer>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchAdd" :loading="saving">批量添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTagLibrary, createTag, updateTag, deleteTag, batchCreateTags } from '@/api/tagLibrary'
import { useTagLibraryStore } from '@/stores/tagLibrary'

const tagStore = useTagLibraryStore()
const dimensions = [
  { label: '题材标签', value: 'genre' },
  { label: '风格标签', value: 'style' },
  { label: '核心元素', value: 'element' },
  { label: '人物类型', value: 'character' }
]

const activeDimension = ref('genre')
const tags = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const showBatchDialog = ref(false)
const saving = ref(false)
const editingTag = ref(null)
const batchText = ref('')

const tagForm = ref({ name: '', description: '', sort_order: 0 })

async function fetchTags() {
  loading.value = true
  try {
    const data = await getTagLibrary({ dimension: activeDimension.value, page: 1, page_size: 200 })
    tags.value = data.items || data
  } catch { /* handled */ } finally {
    loading.value = false
  }
}

function editTag(row) {
  editingTag.value = row
  tagForm.value = { name: row.name, description: row.description || '', sort_order: row.sort_order || 0 }
  showAddDialog.value = true
}

async function handleSave() {
  if (!tagForm.value.name) {
    ElMessage.warning('请输入标签名称')
    return
  }
  saving.value = true
  try {
    if (editingTag.value) {
      await updateTag(editingTag.value.id, tagForm.value)
      ElMessage.success('更新成功')
    } else {
      await createTag({ ...tagForm.value, dimension: activeDimension.value })
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    editingTag.value = null
    tagForm.value = { name: '', description: '', sort_order: 0 }
    await fetchTags()
    tagStore.refresh()
  } catch { /* handled */ } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除标签「${row.name}」？`, '确认', { type: 'warning' })
  await deleteTag(row.id)
  ElMessage.success('删除成功')
  fetchTags()
  tagStore.refresh()
}

async function handleBatchAdd() {
  const names = batchText.value.split('\n').map(s => s.trim()).filter(Boolean)
  if (names.length === 0) {
    ElMessage.warning('请输入至少一个标签')
    return
  }
  saving.value = true
  try {
    await batchCreateTags({
      tags: names.map(name => ({ name, dimension: activeDimension.value }))
    })
    ElMessage.success(`成功添加 ${names.length} 个标签`)
    showBatchDialog.value = false
    batchText.value = ''
    fetchTags()
    tagStore.refresh()
  } catch { /* handled */ } finally {
    saving.value = false
  }
}

onMounted(fetchTags)
</script>
