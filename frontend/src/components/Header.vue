<template>
  <div class="header">
    <div class="inner-header">
      <div>
        Pi-cam - version 0.0.1
      </div>
      <div>
        <ul>
          <li v-if="$store.state.uid==null">
            <router-link to="/login">Login</router-link>
          </li>
          <li v-if="$store.state.uid!=null">
            <router-link to="/stream">Stream</router-link>
          </li>
          <li v-if="$store.state.uid!=null">
            <router-link to="/">Captures</router-link>
          </li>
          <li v-if="$store.state.uid!=null">
            <router-link
              to="/"
              @click.native="doLogout"
            >Logout</router-link>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  name: "Header",
  props: {},
  data() {
    return {};
  },
  mounted() {},
  methods: {
    doLogout() {
      this.axios
        .post("/api/logout", {})
        .then(() => {
          console.log("success");
        })
        .catch(() => {
          console.log("error");
        })
        .finally(() => {
          this.$store.commit("logout");
          this.$router.push({ name: "Login" });
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.header {
  width: 100%;
}
.inner-header {
  background-color: var(--header-bg-color);
  color: var(--main-bg-color);
  height: 5em;
  padding: 0 0 0 1.4em;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  font-size: 1.2em;
}
.inner-header ul {
  list-style-type: none;
  display: flex;
}
.inner-header ul li {
  padding: 0 1.4em 0 0;
  font-size: 0.9em;
}
a {
  color: white;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
</style>
