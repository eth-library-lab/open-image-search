<template>
<v-card
  flat
  tile
  dense
  :height="height">
  <v-app-bar 
    app
    color="primary"
    dark>
    <GSLogo color="white" :size="height+15"/> 
    <v-spacer></v-spacer>

    <v-btn
        target="_blank"
        text
    >
      <v-icon>mdi-menu</v-icon>
    </v-btn>
  <!-- </v-toolbar> -->
  </v-app-bar>
</v-card>
</template>

<script>
import GSLogo from '@/components/GSLogo.vue';

export default {
    components: {
        GSLogo
    },
    computed: {
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