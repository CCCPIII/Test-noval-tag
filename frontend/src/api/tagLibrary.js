/** 标签库管理 API */
import request from './request'

/** 获取标签库列表 */
export function getTagLibrary(params) {
  return request.get('/tag-library/', { params })
}

/** 获取按维度分组的标签 */
export function getGroupedTags() {
  return request.get('/tag-library/grouped')
}

/** 添加标签到标签库 */
export function createTag(data) {
  return request.post('/tag-library/', data)
}

/** 批量添加标签 */
export function batchCreateTags(data) {
  return request.post('/tag-library/batch', data)
}

/** 更新标签库条目 */
export function updateTag(id, data) {
  return request.put(`/tag-library/${id}`, data)
}

/** 删除标签库条目 */
export function deleteTag(id) {
  return request.delete(`/tag-library/${id}`)
}
