/** 小说相关 API */
import request from './request'

/** 上传小说文件 */
export function uploadNovel(formData, onProgress) {
  return request.post('/novels/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  })
}

/** 手动提交小说文本 */
export function submitText(data) {
  return request.post('/novels/text', data)
}

/** 获取小说列表 */
export function getNovelList(params) {
  return request.get('/novels/', { params })
}

/** 获取小说详情 */
export function getNovelDetail(id) {
  return request.get(`/novels/${id}`)
}

/** 删除小说 */
export function deleteNovel(id) {
  return request.delete(`/novels/${id}`)
}
