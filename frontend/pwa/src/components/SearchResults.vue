<template>
    <v-container 
        justify="center"
        align="center"
        align-self="center"
        align-contents="center"
        >
        <div >
        <v-row justify="center" >
            <v-col 
                align="center"
                xs="12" 
                sm="12" 
                md="10" 
                lg="8">

                <v-row
                  justify="center"
                  >
                  <v-col
                    class=""
                    cols="11"
                    >
                    <h3>Search Results</h3>
                  </v-col>
                  <v-col
                    cols="1"
                    justify="right"
                    
                    >
                    <v-btn
                      v-if="!isSavedSearchResult"
                      icon
                      title="save a shareable link to these results"
                      @click="onSaveSearchResults"
                      >
                      <v-icon>mdi-floppy</v-icon>
                      </v-btn>
                    <v-btn
                      v-if="isSavedSearchResult"
                      icon
                      title="show the shareable link for these results"
                      @click="toggleLink"
                      >
                      <v-icon>mdi-link</v-icon>
                      </v-btn>
                  </v-col>
                </v-row>
                <v-row 
                  class="my-0 py-0"
                  v-if="showLink"
                  justify="center">
                  <ResultsLink :resultsUrl="resultsUrl" />
                </v-row>

        <v-row 
            justify="center"
            align="center"
            class="my-0"
            >
            <v-col 
                class="results-wrapper my-0"
                justify="center"
                align="center"
                >
                <v-card
                    class="d-flex align-content-start flex-wrap justify-center"
                    color="white"
                    flat
                    over
                    >
                    <div v-for="object in searchResults"
                        :key="object.id">
                        <HoverTooltip
                            :object="object"
                            >
                            <v-card

                                :href="object.record_url"
                                target="_blank"
                                class="pa-2 ma-1 justify-center"
                                max-width="300"
                                align="center" 
                                justify="center"
                                elevation="1"
                                outlined>
                                <div>
                                    <p>{{ object.title }}</p>
                                    <v-img v-bind:src="object.image_url" max-height="300" max-width="300" />
                                </div>   
                            </v-card>
                        </HoverTooltip>
                    </div>
                </v-card>
            </v-col>    
        </v-row>
        </v-col>
        </v-row>
        </div>
    </v-container>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

import HoverTooltip from '@/components/HoverTooltip.vue';
import ResultsLink from '@/components/ResultsLink.vue';
export default {
    props: {
        searchResults: {
            type: Array,
            required: true
        },
        searchResultId: {
            type: String,
            required: false
        }
    },
    data() {
        return {
          showLink: false
        }
    },
    components:{ HoverTooltip, 
                  ResultsLink
    },
    computed: {
        ...mapGetters(['getIsLoading']),
        resultsUrl(){
          return process.env.VUE_APP_BASE_URL + '/searchresult/'+ this.searchResultId
        },
        isSavedSearchResult() {
          return this.$route.name == 'ViewSearchResult'
        }
    },
    methods:{
      ...mapActions(['saveSearchResults',]),
      onSaveSearchResults() {
        this.showLink = true
        this.saveSearchResults()
      },
      toggleLink() {
        this.showLink = !this.showLink
      }
    }
}
</script>

<style lang="css" scoped>
.results-wrapper {
  overflow-y: auto;
  height: 45vh;
  display: flex;
  flex-flow: column;
  align-items: center;
  margin: 10px;
  padding: 4px;
}
</style>