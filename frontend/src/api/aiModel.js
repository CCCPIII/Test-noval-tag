/** AI模型管理 API */
import request from './request'

/** 获取模型列表 */
export function getModels(params) {
  return request.get('/ai-models/', { params })
}

/** 获取模型详情 */
export function getModel(id) {
  return request.get(`/ai-models/${id}`)
}

/** 创建模型配置 */
export function createModel(data) {
  return request.post('/ai-models/', data)
}

/** 更新模型配置 */
export function updateModel(id, data) {
  return request.put(`/ai-models/${id}`, data)
}

/** 删除模型 */
export function deleteModel(id) {
  return request.delete(`/ai-models/${id}`)
}

/** 测试模型连接 */
export function testModel(id, data) {
  return request.post(`/ai-models/${id}/test`, data)
}
