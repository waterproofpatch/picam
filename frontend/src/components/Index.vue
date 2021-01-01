<template>
  <div>
    <h2 v-if="error">Error: {{ error }}</h2>
    <h2 v-if="success">Success: {{ success }}</h2>

    <center>
      <a
        v-if="takingCapture"
        class="cam-ui-button"
        href="#"
        v-on:click.prevent=""
      >Taking capture...</a>
      <a
        v-else
        class="cam-ui-button"
        href="#"
        v-on:click.prevent="startCapture"
      >Capture</a>
    </center>

    <!-- spinning loading wheel -->
    <center>
      <div
        v-if="loading"
        class="loader"
      ></div>
    </center>

    <!-- print a message if no images are availabel -->
    <p v-if="images.length == 0 && !loading">No captures.</p>

    <!-- show each item -->
    <section class="cards">
      <div
        v-for="image in images"
        v-bind:key="image.id"
        class="card"
      >
        <div class="card-header">
          <a v-bind:href="image.url">
            <div>
              {{image.id}} - {{image.created_on}}
            </div>
          </a>
          <div>
            <a
              v-on:click.stop="deleteCapture(image.id)"
              href="#"
            >
              <span style="color: white;">
                <font-awesome-icon :icon="['fas', 'trash']" />
              </span>
            </a>
          </div>
        </div>
        <div class="card-main">
          <div class="main-description">
            <a v-bind:href="image.url">
              <img
                v-bind:src=image.url
                width=100%
                height=100%
              >
            </a>
            <!-- {{image.url}} -->
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
/* eslint-disable */
export default {
  name: "Index",
  props: {},
  data() {
    return {
      images: [], // from backend
      error: null,
      success: null,
      loading: false,
      takingCapture: false,
    };
  },
  mounted() {
    this.getImages();
  },
  methods: {
    deleteCapture: function (id) {
      console.log("Deleting " + id);
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
        .finally(() => {});
    },
    startCapture: function () {
      this.takingCapture = true;
      this.error = null;
      this.axios
        .post("/api/images")
        .then((response) => {
          this.images = response.data;
          console.log(this.images);
        })
        .catch((error) => {
          console.log(error);
          this.error = error.response.data.error;
        })
        .finally(() => {
          this.takingCapture = false;
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
          if (error.response.status == 500) {
            this.error = "Internal server error.";
          } else {
            this.error = error.response.data.error;
          }
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
@media screen and (min-width: 40em) {
  .card {
    max-width: calc(75% - 1em);
  }
}
.cards {
  display: flex;
  flex-wrap: wrap;
  padding-top: 20px;
}

.card {
  width: 250px; /* Set width of cards */
  height: 250px;
  display: flex; /* Children use Flexbox */
  flex-direction: column; /* Rotate Axis */
  border-radius: 4px; /* Slightly Curve edges */
  overflow: hidden; /* Fixes the corners */
  margin: 5px; /* Add space between cards */
  background: white;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}
.card:hover {
  box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  color: white;
  font-weight: 600;
  background-color: #409fbf;
  padding: 5px 10px;
}

.card-main {
  display: flex; /* Children use Flexbox */
  flex-direction: column; /* Rotate Axis to Vertical */
  justify-content: center; /* Group Children in Center */
  align-items: center; /* Group Children in Center (on cross axis) */
}

.main-description {
  color: black;
  text-align: center;
}

.cam-ui-button {
  margin-top: 10px;
  background-color: var(--button-bg-color);
  border-radius: 28px;
  border: 1px solid #18ab29;
  display: inline-block;
  cursor: pointer;
  color: #ffffff;
  font-family: Arial;
  font-size: 17px;
  padding: 16px 31px;
  text-decoration: none;
  text-shadow: 0px 1px 0px #2f6627;
}
.cam-ui-button:hover {
  background-color: var(--button-bg-color-hover);
}
.cam-ui-button:active {
  position: relative;
  top: 1px;
}
</style>
