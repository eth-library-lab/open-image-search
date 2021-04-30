<template>
<div>
    <div
      v-if="resultsLoaded">
      <v-container class="my-0 py-0" >
        <v-row 
            class="my-0 pa-0"
            justify="center">
            <v-col
                class="my-0 pa-0"
                align="center"
                xs="11" 
                sm="10" 
                md="10" 
                lg="8">
                <v-card 
                  flat>
                  <v-card-text>
                    Original Image
                  </v-card-text>
                  <v-img 
                    class="ma-1"
                    max-height="300" 
                    max-width="300" 
                    :src="getSelectedFile"></v-img>
                </v-card>
            </v-col>
        </v-row>
      </v-container>
        <SearchResults
            :searchResults="searchResults"
            :searchResultId="searchResultId" />
    </div>
    <Spinner
      v-if="getIsLoading"
      message="loading saved search result"
    />
    <Snackbar />
    <Footer v-if="!resultsLoaded"/>
</div>
</template>

<script>
import { mapGetters, mapActions} from 'vuex'
import Footer from '@/components/Footer.vue';
import SearchResults from '@/components/SearchResults.vue';
import Snackbar from '@/components/Snackbar.vue';
import Spinner from '@/components/Spinner.vue';

export default {
  components: {
    Footer,
    SearchResults,
    Snackbar,
    Spinner
  },
  computed: {
    ...mapGetters(['resultsLoaded',
                    'getIsLoading',
                    'getSelectedFile'
                    ]),
    searchResults() {
      return this.$store.getters.getSearchResults
    },
    routeSearchId() {
      return this.$route.params.id
    },
    isResultsView() {
      return this.$route.name == 'SearchResult'
    }
  },
  methods: {
    ...mapActions(['showSnackbar',
                   'changeSearchResultId',
                   'loadSearchResults']),

  },
  mounted() {
    console.log('in created')
    this.changeSearchResultId(this.$route.params.id)
    this.loadSearchResults(this.$route.params.id)
  }
}

</script>

<style scoped>

.tight {
  padding:3px;
  margin-bottom:3px;
}
</style>
