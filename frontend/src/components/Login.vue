<template>
  <div>
    <h2 v-if="error">Error: {{error}}</h2>
    <center>
      <p>Login</p>
    </center>
    <div class="form-container">
      <form class="form form-auth">
        <div class="form-field">
          <input
            placeholder="Email"
            type="text"
            v-model="email"
          >
        </div>
        <div class="form-field">
          <input
            placeholder="Password"
            type="password"
            v-model="password"
          >
        </div>
        <div class="form-field">
          <input
            v-if="logging_in"
            class="btn"
            type="submit"
            value="Processing..."
            v-on:click.prevent="doLogin"
          >
          <input
            v-else
            class="btn"
            type="submit"
            value="Login"
            v-on:click.prevent="doLogin"
          >
        </div>
      </form>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  name: "Login",
  props: {},
  data() {
    return {
      logging_in: false,
      error: null,
      email: "",
      password: "",
    };
  },
  mounted() {
    if (this.$route.params.reason === 1) {
      // try and refresh our token, and try again
      this.error = "Session expired. Please log in again.";
    }
    if (this.$route.params.reason === 2) {
      this.error = "Invalid email or password. Try again.";
    }
  },
  methods: {
    doLogin() {
      this.logging_in = true;
      this.axios
        .post("/api/login", {
          email: this.email,
          password: this.password,
        })
        .then((response) => {
          this.$store.commit("login", {
            uid: response.data.uid,
            email: response.data.email,
          });
          this.$router.push("/");
        })
        .catch((error) => {
          if (error.response.status == 400) {
            this.error = error.response.data.error;
          } else if (error.response.status == 401) {
            this.error = error.response.data.error;
          } else {
            this.error = error.response.status;
          }
        })
        .finally((response) => {
          this.logging_in = false;
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
