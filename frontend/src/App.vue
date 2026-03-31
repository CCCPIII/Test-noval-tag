<template>
  <el-container class="app-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <h1>AI小说总结与标签生成系统</h1>
      <el-button type="info" plain size="small" @click="$router.push('/user')">
        <el-icon><User /></el-icon>
        登录（预留）
      </el-button>
    </el-header>

    <el-container>
      <!-- 侧边导航菜单 -->
      <el-aside width="200px" class="app-aside">
        <el-menu
          :default-active="activeMenu"
          router
          :collapse="false"
        >
          <el-menu-item index="/">
            <el-icon><Document /></el-icon>
            <span>小说列表</span>
          </el-menu-item>
          <el-menu-item index="/upload">
            <el-icon><Upload /></el-icon>
            <span>上传小说</span>
          </el-menu-item>
          <el-menu-item index="/search">
            <el-icon><Search /></el-icon>
            <span>搜索</span>
          </el-menu-item>
          <el-menu-item index="/tag-library">
            <el-icon><Collection /></el-icon>
            <span>标签库管理</span>
          </el-menu-item>
          <el-menu-item index="/ai-models">
            <el-icon><Setting /></el-icon>
            <span>AI模型管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => {
  // 对于详情页，高亮"小说列表"菜单项
  if (route.path.startsWith('/novel/')) return '/'
  return route.path
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  flex-direction: column;
}
.app-aside {
  height: calc(100vh - 60px);
  overflow-y: auto;
}
.app-main {
  height: calc(100vh - 60px);
}
.el-menu {
  border-right: none;
}
</style>
