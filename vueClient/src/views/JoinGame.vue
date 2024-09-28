<template>
  <main class="overflow-scroll w-100">
    <h1 class="page-title p-3 mt-5">Join game</h1>

    <h6 class="m-3 text-center mt-5">
      In this page, you can join KahootClone games as a participant.
    </h6>
    <h6 class="m-3 text-center mb-5">
      Enter the Game ID of the game you want to join and a unique Alias to
      identify you.
    </h6>

    <join-form></join-form>
  </main>
</template>

<script>
import JoinForm from "../components/JoinForm.vue";

export default {
  components: {
    "join-form": JoinForm,
  },
  created() {
    document.title = "Join Game";
  },
};
</script>
