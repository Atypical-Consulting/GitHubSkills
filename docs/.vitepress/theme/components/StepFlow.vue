<script setup lang="ts">
defineProps<{
  steps: Array<{ icon: string; title: string; desc: string }>
}>()
</script>

<template>
  <div class="step-flow">
    <div v-for="(step, i) in steps" :key="i" class="step-flow__item">
      <div class="step-flow__circle">{{ step.icon }}</div>
      <div class="step-flow__content">
        <div class="step-flow__title">{{ step.title }}</div>
        <div class="step-flow__desc">{{ step.desc }}</div>
      </div>
      <div v-if="i < steps.length - 1" class="step-flow__arrow">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.step-flow {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 24px 0;
  overflow-x: auto;
}

.step-flow__item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.step-flow__circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--vp-c-brand-soft);
  border: 2px solid var(--vp-c-brand-1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.step-flow__content {
  min-width: 0;
}

.step-flow__title {
  font-weight: 600;
  font-size: 14px;
  color: var(--vp-c-text-1);
}

.step-flow__desc {
  font-size: 12px;
  color: var(--vp-c-text-2);
  max-width: 120px;
}

.step-flow__arrow {
  color: var(--vp-c-text-3);
  flex-shrink: 0;
  margin: 0 4px;
}

@media (max-width: 768px) {
  .step-flow {
    flex-direction: column;
    align-items: stretch;
  }

  .step-flow__arrow {
    transform: rotate(90deg);
    align-self: center;
    margin: 4px 0;
  }

  .step-flow__desc {
    max-width: none;
  }
}
</style>
