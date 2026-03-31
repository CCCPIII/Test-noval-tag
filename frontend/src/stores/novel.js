/** 小说状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNovelStore = defineStore('novel', () => {
  const currentNovel = ref(null)
  const novelList = ref([])
  const total = ref(0)
  const loading = ref(false)

  function setCurrentNovel(novel) {
    currentNovel.value = novel
  }

  function clearCurrentNovel() {
    currentNovel.value = null
  }

  return { currentNovel, novelList, total, loading, setCurrentNovel, clearCurrentNovel }
})
