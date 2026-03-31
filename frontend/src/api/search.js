/** 搜索相关 API */
import request from './request'

/** 按名称搜索 */
export function searchByName(params) {
  return request.get('/search/by-name', { params })
}

/** 按标签搜索 */
export function searchByTags(params) {
  return request.get('/search/by-tags', { params })
}
