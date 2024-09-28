<template>
  <form @submit.prevent="registerParticipantInGame">
    <div
      class="d-flex flex-column justify-content-center align-items-center p-3"
    >
      <div
        class="d-flex flex-column justify-content-center align-items-center p-4 alert alert-info join-form"
      >
        <div class="form-group form-outline mb-2">
          <label class="form-label" for="publicId"
            >{{ publicIdFieldName }}:</label
          >
          <input
            v-model="publicId"
            required
            type="text"
            id="publicId"
            class="form-control form-control-lg"
          />
        </div>

        <div class="form-group form-outline mb-2 mt-3">
          <label class="form-label" for="alias">{{ aliasFieldName }}:</label>
          <input
            v-model="alias"
            required
            type="text"
            id="alias"
            class="form-control form-control-lg"
          />
        </div>

        <p class="text-danger text-center m-2">{{ badparticipanterror }}</p>
        <button class="btn btn-primary btn-lg m-2" type="submit">Submit</button>
      </div>
    </div>
  </form>
</template>

<script>
import axios from "axios";

const API_PARTICIPANTS = import.meta.env.VITE_DJANGOURL + "/api/participant/";

export default {
  data() {
    return {
      publicIdFieldName: "Game ID",
      aliasFieldName: "Alias",
      publicId: "",
      alias: "",
      badparticipanterror: "",
    };
  },
  methods: {
    async registerParticipantInGame() {
      try {
        await axios
          .post(API_PARTICIPANTS, {
            game: this.publicId,
            alias: this.alias,
          })
          .then((response) => {
            if (response.status == 201) {
              const participant = response.data;
              console.log(participant);
              this.$store.commit("setParticipant", participant);
              this.$router.push("/waiting");
            }
          });
      } catch (error) {
        console.error(error);
        const data = error.response.data;
        if (data.includes("Some value is None")) {
          this.badparticipanterror = "Incorrect Game ID";
        } else {
          // "" + data is a hack to convert the data to a string if it is not already
          this.badparticipanterror = "" + data;
        }
        // this.badparticipanterror =
        //   error.response.status == 403 ? data[0] : "Incorrect Public Id.";
      }
    },
  },
};
</script>
