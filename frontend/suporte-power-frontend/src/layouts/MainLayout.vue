<template>
  <div>
    <Header />
    <div class="d-flex">
      <Sidebar />
      <main class="p-4 flex-grow-1">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
    import Header from '../components/Header.vue'
    import Sidebar from '../components/Sidebar.vue'
</script>
