/** 导出相关 API */
import request from './request'

/** 导出单个小说的总结和标签 */
export function exportNovel(novelId, data) {
  return request.post(`/export/${novelId}`, data, { responseType: 'blob' })
}

/** 批量导出 */
export function batchExport(data) {
  return request.post('/export/batch', data, { responseType: 'blob' })
}
