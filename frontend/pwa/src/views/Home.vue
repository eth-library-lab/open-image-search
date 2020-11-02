<template>
<div>
    <ImageSelector class="mt-4" />
    <v-container v-if="isFileSelected & !resultsLoaded">
      <v-row align="center"
        justify="center">
        <v-col cols="10" align="center">
          <v-btn class="align-center"
            color="primary"
            elevation="2">
            Upload
          </v-btn>
        </v-col>
      </v-row>
    </v-container>  
    <SearchResults v-if="resultsLoaded" :searchResults="getSearchResults" />
    <Footer v-if="!isFileSelected" />
</div>
</template>

<script>
import { mapGetters } from 'vuex'
import ImageSelector from '@/components/ImageSelector.vue';
import Footer from '@/components/Footer.vue';
import SearchResults from '@/components/SearchResults.vue';


export default {
  components: {
    ImageSelector,
    Footer,
    SearchResults
  },
  computed: {
    ...mapGetters(['isFileSelected']),
    getSearchResults() {
      return this.$store.getters.getSearchResults
    },
    resultsLoaded() {
      return this.$store.getters.resultsLoaded
    },
    getUploadStatus() {
      return this.$store.getters.getUploadStatus
    }
  }
}

</script>

<style scoped>

.tight {
  padding:3px;
  margin-bottom:3px;
}
</style>
