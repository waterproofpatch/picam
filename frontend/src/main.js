import Vue from "vue";
import App from "./App.vue";
import Login from "./components/Login.vue";
import Index from "./components/Index.vue";
import Stream from "./components/Stream.vue";

// fontawesome
import { library } from "@fortawesome/fontawesome-svg-core";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

library.add(faArrowLeft);
library.add(faTrash);
library.add(faPlus);

Vue.component("font-awesome-icon", FontAwesomeIcon);

// Vuex store
import store from "./store";

Vue.config.productionTip = false;

// axios
import axios from "axios";
import VueAxios from "vue-axios";

Vue.use(VueAxios, axios);
// end axios

// vue router
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/login",
    component: Login,
    name: "Login",
  },
  {
    path: "/stream",
    component: Stream,
    name: "Stream",
  },
  {
    path: "/",
    component: Index,
    name: "Index",
  },
];

const router = new VueRouter({
  routes, // short for `routes: routes`
});

// nav guard to prompt user to login
router.beforeEach((to, from, next) => {
  if (to.name === "Index" && store.uid === null) {
    // clear out any browser state that would confuse the user into thinking
    // they were still logged in

    /* eslint no-console: ["error", { allow: ["warn", "error"] }] */
    console.warn(
      "Requested 'Index', but had no uid. Logging out then back in."
    );
    store.commit("logout");
    next({
      name: "Login",
    });
  } else {
    next();
  }
});
// done vue router

// Add a response interceptor
axios.interceptors.response.use(
  function(response) {
    // Do something with response data
    return response;
  },
  function(error) {
    // expired token
    if (error.response.status === 401) {
      store.commit("logout");
      router.push("login");
    }
    // invalid creds
    if (error.response.status === 403) {
      store.commit("logout");
      router.push("login");
    }
    if (error.response.status === 422) {
      store.commit("logout");
      router.push("login");
    }
    return Promise.reject(error);
  }
);

// end axios interceptors
new Vue({
  render: (h) => h(App),
  router,
  store,
  beforeCreate() {
    this.$store.commit("initStore");
  },
}).$mount("#app");
