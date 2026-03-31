/** 标签库状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getGroupedTags } from '@/api/tagLibrary'

export const useTagLibraryStore = defineStore('tagLibrary', () => {
  const groupedTags = ref({
    genre: [],
    style: [],
    element: [],
    character: []
  })
  const loading = ref(false)
  const loaded = ref(false)

  /** 从服务器加载标签库数据 */
  async function fetchGroupedTags() {
    if (loaded.value) return
    loading.value = true
    try {
      const data = await getGroupedTags()
      groupedTags.value = data
      loaded.value = true
    } catch {
      // 错误已被拦截器处理
    } finally {
      loading.value = false
    }
  }

  /** 强制刷新 */
  async function refresh() {
    loaded.value = false
    await fetchGroupedTags()
  }

  return { groupedTags, loading, loaded, fetchGroupedTags, refresh }
})
