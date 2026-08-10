<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast-container" :class="toastType" @click="hide">
        <div class="toast-message">{{ message }}</div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const toastType = ref('info')
let timer = null

function show(msg, type = 'info', duration = 3000) {
  if (timer) clearTimeout(timer)
  message.value = msg
  toastType.value = type
  visible.value = true
  timer = setTimeout(() => {
    visible.value = false
  }, duration)
}

function hide() {
  visible.value = false
  if (timer) clearTimeout(timer)
}

// 暴露给父组件使用
defineExpose({ show, hide })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  z-index: 9999;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.toast-container.info {
  background-color: var(--primary-color, #4285f4);
  color: white;
}

.toast-container.success {
  background-color: var(--secondary-color, #34a853);
  color: white;
}

.toast-container.error {
  background-color: var(--accent-color, #ea4335);
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
