<template>
  <div>
    <div v-for="(group, dim) in groupedTags" :key="dim" class="tag-group">
      <div class="tag-group-label">{{ dimensionLabel(dim) }}</div>
      <template v-for="tag in group" :key="tag.tag_id">
        <el-tooltip
          v-if="tag.is_controversial && tag.controversy_note"
          :content="tag.controversy_note"
          placement="top"
        >
          <el-tag
            :class="['tag-' + dim, 'tag-controversial']"
            style="cursor: pointer"
            @click="$emit('tagClick', tag)"
          >
            {{ tag.tag_name }}
          </el-tag>
        </el-tooltip>
        <el-tag
          v-else
          :class="'tag-' + dim"
          style="cursor: pointer"
          @click="$emit('tagClick', tag)"
        >
          {{ tag.tag_name }}
        </el-tag>
      </template>
      <span v-if="group.length === 0" style="color: #c0c4cc; font-size: 13px">暂无标签</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tags: { type: Array, default: () => [] }
})

defineEmits(['tagClick'])

const groupedTags = computed(() => {
  const groups = { genre: [], style: [], element: [], character: [], exclusive: [] }
  for (const tag of props.tags) {
    const dim = tag.dimension || 'genre'
    if (groups[dim]) groups[dim].push(tag)
    else groups[dim] = [tag]
  }
  // 移除空的非必要分组
  const result = {}
  for (const [k, v] of Object.entries(groups)) {
    if (v.length > 0 || ['genre', 'style', 'element', 'character'].includes(k)) {
      result[k] = v
    }
  }
  return result
})

function dimensionLabel(dim) {
  const map = {
    genre: '题材标签',
    style: '风格标签',
    element: '核心元素',
    character: '人物类型',
    exclusive: '专属标签'
  }
  return map[dim] || dim
}
</script>
