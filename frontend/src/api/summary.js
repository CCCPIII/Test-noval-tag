/** 总结相关 API */
import request from './request'

/** 生成总结 */
export function generateSummary(novelId, data) {
  return request.post(`/novels/${novelId}/summary/generate`, data)
}

/** 获取小说所有总结 */
export function getSummaries(novelId) {
  return request.get(`/novels/${novelId}/summaries`)
}

/** 编辑总结 */
export function updateSummary(summaryId, data) {
  return request.put(`/novels/summaries/${summaryId}`, data)
}

/** 获取分段处理进度 */
export function getProgress(novelId) {
  return request.get(`/novels/${novelId}/summary/progress`)
}
