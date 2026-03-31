import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'NovelList',
    component: () => import('@/views/NovelList.vue'),
    meta: { title: '小说列表' }
  },
  {
    path: '/upload',
    name: 'NovelUpload',
    component: () => import('@/views/NovelUpload.vue'),
    meta: { title: '上传小说' }
  },
  {
    path: '/novel/:id',
    name: 'NovelDetail',
    component: () => import('@/views/NovelDetail.vue'),
    meta: { title: '小说详情' }
  },
  {
    path: '/search',
    name: 'SearchPage',
    component: () => import('@/views/SearchPage.vue'),
    meta: { title: '搜索' }
  },
  {
    path: '/tag-library',
    name: 'TagLibrary',
    component: () => import('@/views/TagLibrary.vue'),
    meta: { title: '标签库管理' }
  },
  {
    path: '/ai-models',
    name: 'AIModelManage',
    component: () => import('@/views/AIModelManage.vue'),
    meta: { title: 'AI模型管理' }
  },
  {
    path: '/user',
    name: 'UserPlaceholder',
    component: () => import('@/views/UserPlaceholder.vue'),
    meta: { title: '用户中心' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || ''} - AI小说总结与标签生成系统`
  next()
})

export default router
