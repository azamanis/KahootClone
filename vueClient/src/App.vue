<script setup>
import { RouterView } from "vue-router";
</script>

<template>
  <div class="app-container">
    <header>
      <h1>
        <partial name="page-title"></partial>
      </h1>
    </header>

    <section
      class="d-flex flex-column justify-content-center align-items-center inner-section h-100 block-content"
    >
      <router-view></router-view>
    </section>

    <!-- <footer class="w-100 footer fixed-bottom">
      <hr>
      <p class="text-end w-100">
          Page created by Pablo Cuesta Sierra and Álvaro Zamanilo Sáez.&nbsp;
      </p>
    </footer> -->
  </div>
</template>

<script>
export default {};
</script>

<style scoped></style>
