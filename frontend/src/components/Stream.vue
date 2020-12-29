<template>
  <div>
    <h2 v-if="error">Error: {{ error }}</h2>
    <h2 v-if="success">Success: {{ success }}</h2>

    <img
      width=100%
      height=100%
      src="/api/stream.mjpg"
    />

  </div>
</template>

<script>
/* eslint-disable */
export default {
  name: "Stream",
  props: {},
  data() {
    return {
      error: null,
      success: null,
    };
  },
  mounted() {},
  methods: {},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
