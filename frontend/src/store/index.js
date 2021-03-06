import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    // more official than just email
    uid: null,
    // really just for display purposes
    email: null
  },
  getters: {
    uid: state => state.uid,
    email: state => state.email
  },
  mutations: {
    initStore(state) {
      if (localStorage.getItem("uid")) {
        state.uid = localStorage.getItem("uid");
      }
      if (localStorage.getItem("email")) {
        state.email = localStorage.getItem("email");
      }
    },
    login(state, { uid, email }) {
      localStorage.uid = uid;
      localStorage.email = email;
      state.uid = uid;
      state.email = email;
    },
    logout(state) {
      state.uid = null;
      state.email = null;
      localStorage.removeItem("email");
      localStorage.removeItem("uid");
    }
  }
});

export default store;
