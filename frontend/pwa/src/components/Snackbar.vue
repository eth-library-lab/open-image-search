<template>
<div>
  <v-snackbar
    bottom
    v-model="snackbarState.visible"
    :timeout="snackbarState.timeout"
    :multi-line="snackbarState.multiline === true">
    {{ snackbarState.text }}
      
    <template v-slot:action="{ attrs }">
      <v-btn 
        class="" 
        text 
        dark 
        v-bind="attrs"
        @click="closeSnackbar">Close</v-btn>
    </template>


    
  </v-snackbar>
</div>
</template>

<script>
import { mapActions, mapGetters } from "vuex"

export default {
  methods: {
    ...mapActions(['closeSnackbar',]),
  },
  computed:{
    ...mapGetters(['snackbarState',]),
  }
}

</script>
