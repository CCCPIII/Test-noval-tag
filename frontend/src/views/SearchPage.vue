<template>
  <div class="page-container">
    <h2 class="page-title">搜索</h2>

    <div class="content-card">
      <el-tabs v-model="searchMode">
        <!-- 名称搜索 -->
        <el-tab-pane label="名称搜索" name="name">
          <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 16px">
            <el-input
              v-model="nameKeyword"
              placeholder="输入小说名称..."
              clearable
              style="flex: 1"
              @keyup.enter="doNameSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
            <el-switch v-model="exactMatch" active-text="精准" inactive-text="模糊" />
            <el-button type="primary" @click="doNameSearch" :loading="searching">搜索</el-button>
          </div>
        </el-tab-pane>

        <!-- 标签搜索 -->
        <el-tab-pane label="标签搜索" name="tag">
          <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 16px; flex-wrap: wrap">
            <el-select
              v-model="selectedTagIds"
              multiple
              filterable
              placeholder="选择标签..."
              style="flex: 1; min-width: 300px"
            >
              <el-option-group
                v-for="(tags, dim) in groupedTags"
                :key="dim"
                :label="dimensionLabel(dim)"
              >
                <el-option
                  v-for="tag in tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.id"
                />
              </el-option-group>
            </el-select>
            <el-switch v-model="matchAll" active-text="全部匹配" inactive-text="任一匹配" />
            <el-button type="primary" @click="doTagSearch" :loading="searching">搜索</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 搜索结果 -->
    <div class="content-card" v-if="results.length > 0 || hasSearched">
      <h3 style="margin-bottom: 12px">
        搜索结果
        <span style="color: #909399; font-size: 14px; font-weight: normal">
          （共 {{ total }} 条）
        </span>
      </h3>

      <el-table :data="results" stripe @row-click="goDetail" v-loading="searching">
        <el-table-column prop="title" label="书名" min-width="200" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column label="字数" width="100">
          <template #default="{ row }">{{ formatCount(row.char_count) }}</template>
        </el-table-column>
        <el-table-column label="总结预览" min-width="250">
          <template #default="{ row }">
            <span style="color: #606266">{{ row.summary_preview || '暂无总结' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="t in row.tags" :key="t" size="small" style="margin: 2px">{{ t }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; text-align: right">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="doCurrentSearch"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { searchByName, searchByTags } from '@/api/search'
import { useTagLibraryStore } from '@/stores/tagLibrary'

const router = useRouter()
const route = useRoute()
const tagStore = useTagLibraryStore()

const searchMode = ref('name')
const nameKeyword = ref('')
const exactMatch = ref(false)
const selectedTagIds = ref([])
const matchAll = ref(true)
const results = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searching = ref(false)
const hasSearched = ref(false)
const groupedTags = ref({})

async function doNameSearch() {
  searching.value = true
  hasSearched.value = true
  try {
    const data = await searchByName({
      keyword: nameKeyword.value,
      exact_match: exactMatch.value,
      page: page.value,
      page_size: pageSize.value
    })
    results.value = data.items
    total.value = data.total
  } catch { /* handled */ } finally {
    searching.value = false
  }
}

async function doTagSearch() {
  if (selectedTagIds.value.length === 0) return
  searching.value = true
  hasSearched.value = true
  try {
    const data = await searchByTags({
      tag_ids: selectedTagIds.value.join(','),
      match_all: matchAll.value,
      page: page.value,
      page_size: pageSize.value
    })
    results.value = data.items
    total.value = data.total
  } catch { /* handled */ } finally {
    searching.value = false
  }
}

function doCurrentSearch() {
  if (searchMode.value === 'name') doNameSearch()
  else doTagSearch()
}

function goDetail(row) {
  router.push(`/novel/${row.novel_id}`)
}

function formatCount(n) {
  if (!n) return '0'
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toString()
}

function dimensionLabel(dim) {
  const map = { genre: '题材', style: '风格', element: '核心元素', character: '人物类型' }
  return map[dim] || dim
}

onMounted(async () => {
  await tagStore.fetchGroupedTags()
  groupedTags.value = tagStore.groupedTags
  // 从URL参数恢复搜索状态
  if (route.query.mode === 'tag' && route.query.tagIds) {
    searchMode.value = 'tag'
    selectedTagIds.value = [Number(route.query.tagIds)]
    doTagSearch()
  }
})
</script>
