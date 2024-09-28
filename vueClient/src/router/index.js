import { createRouter, createWebHistory } from "vue-router";
import JoinGame from "../views/JoinGame.vue";
import GuessView from "../views/GuessView.vue";
import WaitingView from "../views/WaitingView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Join-Game",
      component: JoinGame,
    },
    {
      path: "/guess",
      name: "GuessView",
      component: GuessView,
    },
    {
      path: "/waiting",
      name: "WaitingView",
      component: WaitingView,
    },
  ],
});

export default router;
