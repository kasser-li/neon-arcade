<template>
  <div class="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', sans-serif;
  background: #0a0a0a;
  min-height: 100vh;
  color: #fff;
}

.app {
  min-height: 100vh;
}
</style>
