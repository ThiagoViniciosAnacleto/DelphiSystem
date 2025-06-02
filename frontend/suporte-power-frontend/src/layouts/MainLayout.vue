<template>
  <div class="layout">
    <Header />
    <div class="body">
      <Sidebar />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
  import Header from '@/components/Header.vue'
  import Sidebar from '@/components/Sidebar.vue'
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.body {
  display: grid;
  grid-template-columns: 220px 1fr;
  flex: 1;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.content {
  padding: 1rem;
  overflow-y: auto;
  background-color: #121212;
  color: #fff;
}
</style>
