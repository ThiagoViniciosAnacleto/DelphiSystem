<template>
  <div class="layout">
    <Sidebar />
    <div class="main">
      <Header />
      <main class="conteudo">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
    import Header from '../components/Header.vue'
    import Sidebar from '../components/Sidebar.vue'
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #121212;
}

.conteudo {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  color: #fff;
}
</style>