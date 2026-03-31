/** 标签相关 API */
import request from './request'

/** AI生成标签 */
export function generateTags(novelId, data = {}) {
  return request.post(`/novels/${novelId}/tags/generate`, data)
}

/** 获取小说所有标签 */
export function getNovelTags(novelId) {
  return request.get(`/novels/${novelId}/tags`)
}

/** 手动分配标签 */
export function assignTag(novelId, data) {
  return request.post(`/novels/${novelId}/tags/assign`, data)
}

/** 批量分配标签 */
export function batchAssignTags(novelId, data) {
  return request.post(`/novels/${novelId}/tags/batch-assign`, data)
}

/** 移除标签 */
export function removeTag(novelId, tagId) {
  return request.delete(`/novels/${novelId}/tags/${tagId}`)
}

/** 更新争议标签状态 */
export function updateControversy(novelId, tagId, data) {
  return request.put(`/novels/${novelId}/tags/${tagId}/controversy`, data)
}
