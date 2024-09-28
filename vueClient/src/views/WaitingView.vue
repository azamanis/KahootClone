<template>
  <main class="overflow-scroll w-100">
    <div
      class="d-flex flex-column justify-content-center align-items-center p-5"
    >
      <h1 class="page-title p-3 mt-5">Waiting</h1>

      <h2 class="m-5 text-center">
        You joined the Game with ID: {{ publicId }}
      </h2>
      <h2 class="m-5 text-center">Waiting for the game to begin...</h2>
    </div>
  </main>
</template>

<script>
import axios from "axios";

const API_GAME = import.meta.env.VITE_DJANGOURL + "/api/games/";

const WAITING = 1;

export default {
  created() {
    document.title = "Waiting";
  },
  data() {
    return {
      publicId: String(this.$store.getters.getPublicId),
      uuidP: this.$store.getters.getUuidP,
    };
  },
  mounted() {
    if (this.validPage()) {
      this.interval = setInterval(this.getGameState, 1000);
    } else {
      this.$router.push("/");
    }
  },
  unmounted: function () {
    if (this.interval) {
      clearInterval(this.interval);
    }
  },
  methods: {
    validPage() {
      return this.publicId != null && this.uuidP != null;
    },
    async getGameState() {
      try {
        await axios.get(API_GAME + this.publicId).then((response) => {
          const game = response.data;

          if (response.status == 200 && game.state != WAITING) {
            this.$router.push("/guess");
          }
        });
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>
