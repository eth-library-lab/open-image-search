<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="10">

        <v-app-bar
        app
        height="150"
        color="primary"
        dark>
            <GSLogo color="white" size="150"/> 
        <v-spacer></v-spacer>

        <v-btn
            target="_blank"
            text
        >
        <v-icon>mdi-menu</v-icon>
        </v-btn>
        </v-app-bar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import GSLogo from '@/components/GSLogo.vue';

export default {
    components:{
        GSLogo
    }
}
</script>

<style lang="scss" scoped>

</style>