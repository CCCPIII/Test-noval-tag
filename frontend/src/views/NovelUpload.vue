<template>
  <div class="page-container">
    <h2 class="page-title">上传小说</h2>

    <!-- 版权提示 -->
    <el-alert
      title="版权声明"
      description="请确保您上传的小说文本拥有合法版权，系统不承担因上传侵权内容导致的法律责任。"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    />

    <el-tabs v-model="activeTab">
      <!-- 文件上传模式 -->
      <el-tab-pane label="文件上传" name="file">
        <div class="content-card">
          <el-form label-width="80px">
            <el-form-item label="书名">
              <el-input v-model="fileForm.title" placeholder="可选，留空则自动识别文件名" />
            </el-form-item>
            <el-form-item label="作者">
              <el-input v-model="fileForm.author" placeholder="可选" />
            </el-form-item>
          </el-form>

          <el-upload
            ref="uploadRef"
            drag
            multiple
            :limit="10"
            :auto-upload="false"
            :file-list="fileList"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :before-upload="beforeUpload"
            accept=".txt,.pdf"
          >
            <el-icon style="font-size: 48px; color: #909399"><Upload /></el-icon>
            <div style="margin-top: 8px">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div style="color: #909399; font-size: 12px; margin-top: 8px">
                支持 TXT、PDF 格式，单文件最大 200MB，批量上传最多 10 个文件
              </div>
            </template>
          </el-upload>

          <!-- 上传进度 -->
          <el-progress
            v-if="uploading"
            :percentage="uploadProgress"
            :status="uploadProgress === 100 ? 'success' : ''"
            style="margin-top: 16px"
          />

          <el-button
            type="primary"
            :loading="uploading"
            style="margin-top: 16px"
            @click="handleUpload"
            :disabled="fileList.length === 0"
          >
            开始上传
          </el-button>
        </div>
      </el-tab-pane>

      <!-- 文本输入模式 -->
      <el-tab-pane label="文本输入" name="text">
        <div class="content-card">
          <el-form label-width="80px">
            <el-form-item label="书名" required>
              <el-input v-model="textForm.title" placeholder="请输入小说名称" />
            </el-form-item>
            <el-form-item label="作者">
              <el-input v-model="textForm.author" placeholder="可选" />
            </el-form-item>
            <el-form-item label="小说文本" required>
              <el-input
                v-model="textForm.text_content"
                type="textarea"
                :rows="15"
                placeholder="请粘贴小说文本内容..."
                show-word-limit
              />
            </el-form-item>
          </el-form>
          <el-button type="primary" :loading="submitting" @click="handleSubmitText">
            提交文本
          </el-button>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 去重提示弹窗 -->
    <el-dialog v-model="dupDialogVisible" title="发现重复内容" width="450px">
      <p>系统检测到已存在相同的小说记录：</p>
      <p style="font-weight: bold; margin: 12px 0">《{{ dupNovelTitle }}》</p>
      <p>是否直接查看已有结果？</p>
      <template #footer>
        <el-button @click="dupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="goToDuplicate">查看已有结果</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { uploadNovel, submitText } from '@/api/novel'

const router = useRouter()
const activeTab = ref('file')

// 文件上传
const fileForm = ref({ title: '', author: '' })
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)

// 文本输入
const textForm = ref({ title: '', author: '', text_content: '' })
const submitting = ref(false)

// 去重弹窗
const dupDialogVisible = ref(false)
const dupNovelTitle = ref('')
const dupNovelId = ref(null)

function handleFileChange(file, fileListVal) {
  fileList.value = fileListVal
}

function handleExceed() {
  ElMessage.warning('批量上传最多支持10个文件')
}

function beforeUpload(file) {
  const validTypes = ['.txt', '.pdf']
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  if (!validTypes.includes(ext)) {
    ElMessage.error('仅支持TXT、PDF格式')
    return false
  }
  if (file.size > 200 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过200MB')
    return false
  }
  return true
}

async function handleUpload() {
  if (fileList.value.length === 0) return
  uploading.value = true
  uploadProgress.value = 0

  try {
    for (let i = 0; i < fileList.value.length; i++) {
      const formData = new FormData()
      formData.append('file', fileList.value[i].raw)
      if (fileForm.value.title) formData.append('title', fileForm.value.title)
      if (fileForm.value.author) formData.append('author', fileForm.value.author)

      const result = await uploadNovel(formData, (e) => {
        if (e.total) {
          uploadProgress.value = Math.round(
            ((i / fileList.value.length) + (e.loaded / e.total / fileList.value.length)) * 100
          )
        }
      })

      // 检查去重
      if (result.duplicate) {
        dupNovelTitle.value = result.existing_title || '未知'
        dupNovelId.value = result.existing_id
        dupDialogVisible.value = true
        continue
      }
    }
    uploadProgress.value = 100
    ElMessage.success('上传完成')
    setTimeout(() => router.push('/'), 1000)
  } catch { /* handled */ } finally {
    uploading.value = false
  }
}

async function handleSubmitText() {
  if (!textForm.value.title) {
    ElMessage.warning('请输入小说名称')
    return
  }
  if (!textForm.value.text_content) {
    ElMessage.warning('请输入小说文本')
    return
  }
  submitting.value = true
  try {
    const result = await submitText(textForm.value)
    if (result.duplicate) {
      dupNovelTitle.value = result.existing_title || '未知'
      dupNovelId.value = result.existing_id
      dupDialogVisible.value = true
    } else {
      ElMessage.success('提交成功')
      router.push(`/novel/${result.id}`)
    }
  } catch { /* handled */ } finally {
    submitting.value = false
  }
}

function goToDuplicate() {
  dupDialogVisible.value = false
  if (dupNovelId.value) router.push(`/novel/${dupNovelId.value}`)
}
</script>
