<template>
  <el-dialog
    :modelValue="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    :title="modelData ? '编辑模型' : '添加模型'"
    width="600px"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item label="模型名称" required>
        <el-input v-model="form.name" placeholder="如：GPT-4o" />
      </el-form-item>
      <el-form-item label="提供商" required>
        <el-select v-model="form.provider" style="width: 100%">
          <el-option label="OpenAI" value="openai" />
          <el-option label="智谱AI" value="zhipu" />
          <el-option label="本地模型" value="local" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item label="API地址" required>
        <el-input v-model="form.api_url" placeholder="https://api.openai.com/v1/chat/completions" />
      </el-form-item>
      <el-form-item label="API密钥">
        <el-input v-model="form.api_key" type="password" show-password placeholder="可选" />
      </el-form-item>
      <el-form-item label="模型标识" required>
        <el-input v-model="form.model_identifier" placeholder="如：gpt-4o-mini" />
      </el-form-item>
      <el-form-item label="最大Token">
        <el-input-number v-model="form.max_tokens" :min="512" :max="128000" :step="512" />
      </el-form-item>
      <el-form-item label="适配最大字数">
        <el-input-number v-model="form.supported_max_chars" :min="0" :step="10000" />
        <span style="margin-left: 8px; color: #909399">字</span>
      </el-form-item>
      <el-form-item label="速度评级">
        <el-select v-model="form.avg_speed" style="width: 100%">
          <el-option label="快速" value="fast" />
          <el-option label="中等" value="medium" />
          <el-option label="较慢" value="slow" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="准确率说明">
        <el-input v-model="form.accuracy_note" placeholder="如：总结准确率约90%" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createModel, updateModel } from '@/api/aiModel'

const props = defineProps({
  modelValue: Boolean,
  modelData: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue', 'saved'])
const saving = ref(false)

const defaultForm = () => ({
  name: '', provider: 'openai', api_url: '', api_key: '',
  model_identifier: '', max_tokens: 4096, description: '',
  supported_max_chars: null, avg_speed: 'medium', accuracy_note: ''
})

const form = ref(defaultForm())

watch(() => props.modelValue, (val) => {
  if (val && props.modelData) {
    form.value = { ...defaultForm(), ...props.modelData, api_key: '' }
  } else if (val) {
    form.value = defaultForm()
  }
})

async function handleSave() {
  if (!form.value.name || !form.value.api_url || !form.value.model_identifier) {
    ElMessage.warning('请填写必填字段')
    return
  }
  saving.value = true
  try {
    if (props.modelData?.id) {
      await updateModel(props.modelData.id, form.value)
    } else {
      await createModel(form.value)
    }
    ElMessage.success('保存成功')
    emit('update:modelValue', false)
    emit('saved')
  } catch { /* handled */ } finally {
    saving.value = false
  }
}
</script>
