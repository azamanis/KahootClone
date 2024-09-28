import Vuex from "vuex";

export default new Vuex.Store({
  state: {
    publicId: null,
    uuidP: null,
  },
  mutations: {
    setParticipant(state, participant) {
      state.publicId = participant.game;
      state.uuidP = participant.uuidP;
    },
  },
  getters: {
    getPublicId(state) {
      return state.publicId;
    },
    getUuidP(state) {
      return state.uuidP;
    },
  },
});
