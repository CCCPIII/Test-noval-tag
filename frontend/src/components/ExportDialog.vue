<template>
  <el-dialog :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)" title="导出总结与标签" width="400px">
    <el-radio-group v-model="format" style="margin-bottom: 16px">
      <el-radio value="txt">TXT 格式</el-radio>
      <el-radio value="docx">Word 格式</el-radio>
    </el-radio-group>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleExport" :loading="exporting">导出</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { exportNovel } from '@/api/export'

const props = defineProps({
  modelValue: Boolean,
  novelId: { type: [Number, String] }
})

const emit = defineEmits(['update:modelValue'])
const format = ref('txt')
const exporting = ref(false)

async function handleExport() {
  if (!props.novelId) return
  exporting.value = true
  try {
    const blob = await exportNovel(props.novelId, { format: format.value })
    // 触发浏览器下载
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.download = `小说总结_${Date.now()}.${format.value}`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
    emit('update:modelValue', false)
  } catch { /* handled */ } finally {
    exporting.value = false
  }
}
</script>
