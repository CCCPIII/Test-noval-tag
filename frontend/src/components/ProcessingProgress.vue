<template>
  <div class="content-card progress-area">
    <el-progress
      :percentage="progress.progress_percent || 0"
      :status="progress.status === 'done' ? 'success' : progress.status === 'error' ? 'exception' : ''"
      :stroke-width="18"
    />
    <div class="progress-text">
      <template v-if="progress.status === 'processing'">
        处理中：{{ progress.completed_chunks }}/{{ progress.total_chunks }} 段完成
      </template>
      <template v-else-if="progress.status === 'merging'">
        正在合并总结...
      </template>
      <template v-else-if="progress.status === 'done'">
        处理完成
      </template>
      <template v-else-if="progress.status === 'error'">
        处理出错，请重试
      </template>
      <template v-else>
        等待处理...
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getProgress } from '@/api/summary'

const props = defineProps({
  novelId: { type: [Number, String], required: true }
})

const progress = ref({
  total_chunks: 0,
  completed_chunks: 0,
  status: 'processing',
  progress_percent: 0
})

let timer = null

async function fetchProgress() {
  try {
    const data = await getProgress(props.novelId)
    progress.value = data
    if (data.status === 'done' || data.status === 'error') {
      clearInterval(timer)
    }
  } catch { /* ignore */ }
}

onMounted(() => {
  fetchProgress()
  timer = setInterval(fetchProgress, 2000) // 每2秒轮询
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
