<template>
<v-card
  flat
  tile
  dense
  :height="height"
  >
  <v-app-bar 
    app
    color="primary"
    dark>
    <GSLogo color="white" :size="height+15"/> 
    <v-spacer></v-spacer>
    <v-btn
      v-if="this.$route.name !='Home'"
      icon
      exact
      :to="{name:'Home'}"
      title="back to main page"
      >
      <v-icon>mdi-home</v-icon>
    </v-btn>
    <v-btn
      v-if="this.$route.name !='About'"
      icon
      :to="{name:'About'}"
      :title="`see more info\n (v${appVersion})`"
      >
      <v-icon>mdi-information-outline</v-icon>
    </v-btn>  
  <!-- </v-toolbar> -->
  </v-app-bar>
</v-card>
</template>

<script>
import GSLogo from '@/components/GSLogo.vue';
import { mapGetters }  from 'vuex';

export default {
  data() {
    return{

    }
  },
    components: {
        GSLogo
    },
    computed: {
      ...mapGetters(['appVersion',]),
      height() {
        switch (this.$vuetify.breakpoint.name) {
          case 'xs': return 75
          case 'sm': return 85
          case 'md': return 90
          case 'lg': return 95
          case 'xl': return 95
        } return 100
      }
    }
}
</script>

<style lang="scss" scoped>

</style>