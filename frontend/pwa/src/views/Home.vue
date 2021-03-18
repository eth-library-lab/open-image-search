<template>
<div>
    <ImageSelector class="mt-1" />  
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
    ...mapGetters(['isFileSelected', 'resultsLoaded']),
    getSearchResults() {
      return this.$store.getters.getSearchResults
    },
  }
}

</script>

<style scoped>

.tight {
  padding:3px;
  margin-bottom:3px;
}
</style>
