<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { navigation } from './router'
import { useWorkspace } from './stores/workspace'
const route = useRoute()
const store = useWorkspace()
onMounted(() => store.refresh())
</script>
<template>
  <div class="app">
    <aside class="side">
      <div class="brand"><div class="logo">✳</div><div class="brand-text">Meridian<small>CROSS-BORDER INTELLIGENCE</small></div></div>
      <div class="nav-label">工作空间 / WORKSPACE</div>
      <nav class="nav-group" aria-label="主导航"><RouterLink v-for="item in navigation" :key="item.key" :to="item.path" class="nav" :title="item.title"><span class="ni">{{ item.icon }}</span><span>{{ item.title }}</span></RouterLink></nav>
      <div class="sidefoot"><b>◈ &nbsp; 系统状态</b><span :class="{'status-connected': store.health}">{{ store.health ? 'API 已连接 · 演示环境' : 'API 未连接' }}</span><br>外部集成未启用</div>
    </aside>
    <main class="main"><header class="top"><div class="crumb">工作空间 &nbsp; / &nbsp; <strong>{{ route.meta.title }}</strong></div><div class="topright"><span class="tag-demo">● &nbsp; 演示环境 · 非生产</span><a href="/prototype/index.html" target="_blank" rel="noopener" class="context">打开交互原型 ↗</a><span class="avatar">运</span><span class="context">演示用户</span></div></header><div class="content"><RouterView /></div></main>
  </div>
</template>
