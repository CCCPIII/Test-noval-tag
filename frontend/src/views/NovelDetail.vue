<template>
  <div class="page-container" v-loading="loading">
    <div v-if="novel">
      <!-- 小说基本信息 -->
      <div class="content-card">
        <div class="toolbar">
          <div>
            <h2 style="margin-bottom: 8px">{{ novel.title }}</h2>
            <span style="color: #909399">
              作者：{{ novel.author || '未知' }} |
              字数：{{ formatCharCount(novel.char_count) }} |
              状态：<el-tag :type="statusType(novel.status)" size="small">{{ statusLabel(novel.status) }}</el-tag>
            </span>
          </div>
          <div>
            <el-button @click="showExportDialog = true">
              <el-icon><Download /></el-icon> 导出
            </el-button>
            <el-button type="primary" @click="$router.push('/')">返回列表</el-button>
          </div>
        </div>
      </div>

      <!-- 处理进度（处理中时显示） -->
      <ProcessingProgress v-if="novel.status === 'processing'" :novel-id="novel.id" />

      <!-- 总结面板 -->
      <SummaryPanel :novel-id="novel.id" :summaries="summaries" @refresh="fetchDetail" />

      <!-- 标签展示 -->
      <div class="content-card">
        <h3 style="margin-bottom: 12px">标签</h3>
        <TagDisplay :tags="novelTags" @tag-click="goSearchByTag" />
        <el-divider />
        <TagEditor :novel-id="novel.id" :existing-tags="novelTags" @refresh="fetchDetail" />

        <div style="margin-top: 16px">
          <el-button type="primary" plain @click="handleGenerateTags" :loading="generatingTags">
            AI自动生成标签
          </el-button>
        </div>
      </div>
    </div>

    <!-- 导出弹窗 -->
    <ExportDialog v-model="showExportDialog" :novel-id="novel?.id" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getNovelDetail } from '@/api/novel'
import { getSummaries } from '@/api/summary'
import { getNovelTags, generateTags } from '@/api/tag'
import SummaryPanel from '@/components/SummaryPanel.vue'
import TagDisplay from '@/components/TagDisplay.vue'
import TagEditor from '@/components/TagEditor.vue'
import ExportDialog from '@/components/ExportDialog.vue'
import ProcessingProgress from '@/components/ProcessingProgress.vue'

const route = useRoute()
const router = useRouter()
const novel = ref(null)
const summaries = ref([])
const novelTags = ref([])
const loading = ref(false)
const showExportDialog = ref(false)
const generatingTags = ref(false)

async function fetchDetail() {
  loading.value = true
  try {
    const id = route.params.id
    novel.value = await getNovelDetail(id)
    summaries.value = await getSummaries(id)
    novelTags.value = await getNovelTags(id)
  } catch { /* handled */ } finally {
    loading.value = false
  }
}

async function handleGenerateTags() {
  generatingTags.value = true
  try {
    await generateTags(novel.value.id)
    ElMessage.success('标签生成完成')
    await fetchDetail()
  } catch { /* handled */ } finally {
    generatingTags.value = false
  }
}

function goSearchByTag(tag) {
  router.push({ path: '/search', query: { mode: 'tag', tagIds: tag.tag_id } })
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

onMounted(fetchDetail)
</script>
