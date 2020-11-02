<template>
  <v-app>
    <NavBar />
    <v-main class="my-1 py-2">
      <router-view class="my-1 py-1"></router-view>
    </v-main>
  </v-app>
</template>

<script>
import NavBar from '@/components/NavBar.vue';

export default {
  name: 'App',

  components: {
    NavBar,
  },

  data: () => ({
    //
  }),
};
</script>

<style >

</style>
