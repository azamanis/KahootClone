<template>
  <main class="overflow-scroll w-100 vh-fill">
    <div
      v-if="this.isQuestionState() && this.isAllowedAnswer()"
      class="d-flex flex-column container justify-content-center align-items-center w-100 overflow-scroll h-100"
    >
      <h2 class="page-title p-3 mt-5">Select an answer:</h2>

      <div class="row d-flex flex-row justify-content-center w-100">
        <button
          @click="this.postGuess(0)"
          class="col-md-6 alert ans-0 container p-3 m-1 text-center answer-box"
        >
          <h4>A</h4>
        </button>
        <button
          @click="this.postGuess(1)"
          class="col-md-6 alert ans-1 container p-3 m-1 text-center answer-box"
        >
          <h4>B</h4>
        </button>
      </div>
      <div class="row d-flex flex-row justify-content-center w-100">
        <button
          @click="this.postGuess(2)"
          class="col-md-6 alert ans-2 container p-3 m-1 text-center answer-box"
        >
          <h4>C</h4>
        </button>
        <button
          @click="this.postGuess(3)"
          class="col-md-6 alert ans-3 container p-3 m-1 text-center answer-box"
        >
          <h4>D</h4>
        </button>
      </div>

      <p class="text-danger text-center m-2">{{ response_error }}</p>
    </div>

    <h2
      v-if="!this.isAllowedAnswer() && this.isQuestionState()"
      class="d-flex flex-column container justify-content-center align-items-center w-100 vh-fill text-center"
    >
      Answer registered.<br />
      Waiting for the end of the question.
    </h2>
    <h2
      v-if="this.isAnswerState()"
      class="d-flex flex-column container justify-content-center align-items-center w-100 vh-fill text-center"
    >
      Question time ended.<br />
      Waiting for the next question.
    </h2>
  </main>
</template>

answers.

<script>
import axios from "axios";

const API_GUESS = import.meta.env.VITE_DJANGOURL + "/api/guess/";
const API_GAME = import.meta.env.VITE_DJANGOURL + "/api/games/";

// const WAITING = 1;
const QUESTION = 2;
const ANSWER = 3;
const LEADERBOARD = 4;

export default {
  created() {
    document.title = "Playing Game";
  },
  data() {
    return {
      publicId: this.$store.getters.getPublicId,
      uuidP: this.$store.getters.getUuidP,
      answerState: false,
      alreadyAnswered: false,
      numberCurrentQuestion: 0,
      response_error: "",
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

    async postGuess(idx) {
      // console.log("enter post guess: " + idx);
      try {
        await axios
          .post(API_GUESS, {
            game: this.publicId,
            uuidp: this.uuidP,
            answer: idx,
          })
          .then(() => {
            this.setDisallowAnswer();
          });
      } catch (error) {
        const data = error.response.data;
        console.error("An error ocurred while creating Guess: " + data);
        if (data.includes("participant:None")) {
          alert("You are not a participant of this game");
          this.$router.push("/");
        } else if (data.includes("game:None")) {
          alert("This game does not exist");
          this.$router.push("/");
        } else if (data.includes("Some value is None")) {
          this.response_error = "There was an error with your request";
        } else {
          // "" + data is a hack to convert the data to a string if it is not already
          this.response_error = "" + data;
        }
      }
    },

    async getGameState() {
      try {
        await axios
          .get(API_GAME + String(this.$store.getters.getPublicId))
          .then(this.processGameStateResponse);
      } catch (error) {
        console.error(error);
      }
    },

    processGameStateResponse(response) {
      const game = response.data;
      const newQuestion = game.questionNo > this.numberCurrentQuestion;

      if (game.state == ANSWER && this.isQuestionState()) {
        this.setAnswerState();
      } else if (
        game.state == QUESTION &&
        (this.isAnswerState() || newQuestion)
      ) {
        this.setQuestionState();
        this.setAllowAnswer();
        this.numberCurrentQuestion = game.questionNo;
      } else if (game.state == LEADERBOARD) {
        this.$router.push("/");
      }
      // console.log(
      //   "answerState: " +
      //     this.answerState +
      //     ". alreadyAnswered: " +
      //     this.alreadyAnswered
      // );
    },

    // state logic below here -------------------------------------
    // answerState = f , alreadyAnswered = f
    // answerState = f , alreadyAnswered = t
    // answerState = t , alreadyAnswered = -

    setAnswerState() {
      this.answerState = true;
    },
    setQuestionState() {
      this.answerState = false;
    },
    setAllowAnswer() {
      this.alreadyAnswered = false;
    },
    setDisallowAnswer() {
      this.alreadyAnswered = true;
    },

    isAnswerState() {
      return this.answerState;
    },
    isQuestionState() {
      return !this.answerState;
    },
    isAllowedAnswer() {
      return !this.alreadyAnswered;
    },
  },
};
</script>
