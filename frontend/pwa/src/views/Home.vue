<template>
<div>
  <div>
    <ImageSelector />
    <v-container>
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
    <SearchResults />
    <InfoBlock />
    
  </div>
</div>
</template>

<script>
import ImageSelector from '@/components/ImageSelector.vue';
import InfoBlock from '@/components/InfoBlock.vue';
import SearchResults from '@/components/SearchResults.vue';

export default {
  components: {
    ImageSelector,
    InfoBlock,
    SearchResults
  },

}
</script>

<style scoped>


</style>