<script setup lang="ts">
defineProps<{
  type?: 'pass' | 'fail' | 'warn' | 'info' | 'brand' | 'health' | 'issue' | 'action'
  text: string
}>()
</script>

<template>
  <span class="ghs-badge" :class="`ghs-badge--${type ?? 'brand'}`">{{ text }}</span>
</template>

<style scoped>
.ghs-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
}

.ghs-badge--pass  { background: rgba(63, 185, 80, 0.15); color: #3FB950; }
.ghs-badge--fail  { background: rgba(248, 81, 73, 0.15); color: #F85149; }
.ghs-badge--warn  { background: rgba(210, 153, 34, 0.15); color: #D29922; }
.ghs-badge--info  { background: rgba(88, 166, 255, 0.15); color: #58A6FF; }
.ghs-badge--brand { background: rgba(124, 58, 237, 0.15); color: #7C3AED; }

.ghs-badge--health { background: rgba(63, 185, 80, 0.15); color: #3FB950; }
.ghs-badge--issue  { background: rgba(88, 166, 255, 0.15); color: #58A6FF; }
.ghs-badge--action { background: rgba(210, 153, 34, 0.15); color: #D29922; }
</style>
