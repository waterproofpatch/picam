/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
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

/* define the frontend routes here */
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

/* instantiate the router */
const router = new VueRouter({
  routes, // short for `routes: routes`
});

/* nav guard to prompt user to login */
router.beforeEach((to, from, next) => {
  if (to.name === "Index" && store.uid === null) {
    /* clear out any browser state that would confuse the user into thinking
     * they were still logged in
     */

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
    // Return response back to axios user (caller).
    return response;
  },
  /* async so we can 'await' for axios functions to return */
  async function(error) {
    // expired token, we'll try to refresh the token and try again.
    if (error.response.status === 401) {
      var the_response = null;
      /*
       * try and get a new token and replay the request.
       * Await so that we hold the_response until we have legitimate data.
       */
      await axios
        .post("/api/refresh")
        .then(async (response) => {
          store.commit("login", {
            uid: response.data.uid,
            email: response.data.email,
          });
          console.warn("retrying request");
          await axios
            .request(error.config)
            .then((response) => {
              console.warn("returning response to caller...");
              the_response = response;
            })
            .catch((error) => {
              console.error(
                "Got error trying to replay the request with a refreshed token: " +
                  error
              );
            });
        })
        .catch(() => {
          console.error(
            "got expired token when trying to use the refresh token! should give up."
          );
        });
      console.warn("about to ret");
      return the_response;

      // store.commit("logout");
      // router.push({ name: "Login", params: { reason: 1 } });
    }
    // invalid creds
    if (error.response.status === 403) {
      store.commit("logout");
      router.push({ name: "Login", params: { reason: 2 } });
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
