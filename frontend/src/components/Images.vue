<template>
  <div>
    <h2 v-if="error">Error: {{ error }}</h2>
    <h2 v-if="success">Success: {{ success }}</h2>

    <center><button v-on:click="startCapture">Capture</button></center>

    <div
      v-for="image in images"
      v-bind:key="image.id"
    >
      <p>Image {{image.id}}: {{image.url}}</p>
      <button v-on:click="deleteCapture(image.id)">Delete</button>
      <img
        v-bind:src=image.url
        width=256px
        height=256px
      >
    </div>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  name: "Images",
  props: {},
  data() {
    return {
      file: null,
      images: [],
      error: null,
      success: null,
    };
  },
  mounted() {
    this.getImages();
  },
  methods: {
    deleteCapture: function (id) {
      console.log("Deleting " + id);
      this.loading = true;
      this.error = null;
      this.axios
        .delete("/api/images/" + id)
        .then((response) => {
          this.images = response.data;
        })
        .catch((error) => {
          console.log(error);
          this.error = error.response.data.error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    startCapture: function () {
      this.loading = true;
      this.error = null;
      this.axios
        .post("/api/images")
        .then((response) => {
          this.images = response.data;
        })
        .catch((error) => {
          console.log(error);
          this.error = error.response.data.error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    getImages: function () {
      this.loading = true;
      this.error = null;
      this.axios
        .get("/api/images")
        .then((response) => {
          this.images = response.data;
        })
        .catch((error) => {
          this.images = [];
          this.error = error.response.data.error;
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.form-item {
  width: 450px;
  display: flex;
  flex-direction: column;
}
.form-item input[type="text"],
.form-item input[type="password"] {
  border: 1px solid #888;
}
.form-item input[type="text"],
.form-item input[type="password"],
.form-item input[type="submit"] {
  border-radius: 0.25rem;
  padding: 1rem;
  color: var(--input-border-color);
  background-color: #ffffff;
  width: 100%;
}
.form-item input[type="text"]:focus,
.form-item input[type="text"]:hover,
.form-item input[type="password"]:focus,
.form-item input[type="password"]:hover {
  background-color: var(--input-hover-bg-color);
}
.form-item input[type="submit"] {
  background-color: var(--button-bg-color);
  color: white;
  font-weight: bold;
  text-transform: uppercase;
}
.form-item input[type="submit"]:focus,
.form-item input[type="submit"]:hover {
  background-color: black;
}
.form-field {
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  margin-bottom: 2rem;
}
input {
  border: 0;
  color: inherit;
  font: inherit;
  margin: 0;
  outline: 0;
  padding: 0;
  -webkit-transition: background-color 0.3s;
  transition: background-color 0.3s;
}
</style>
