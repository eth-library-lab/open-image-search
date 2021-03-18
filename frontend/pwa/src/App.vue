<template>
  <v-app>
    <NavBar />
    <div>
    <v-main class="">
      <router-view class=""></router-view>
    </v-main>
    </div>
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
