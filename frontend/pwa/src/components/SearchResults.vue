<template>
    <v-container 
        justify="center"
        align="center"
        align-self="center"
        align-contents="center"
        >
        <div >
        <v-row justify="center" >
            <h3>Search Results</h3>
        </v-row>
        <v-row v-if="getIsLoading" 
            justify="center"
            align="center">
            <Spinner />
        </v-row>
        <v-row >
            <v-col class="results-wrapper" >
                <v-card
                    class="d-flex align-content-start flex-wrap justify-center"
                    color="white"
                    flat
                    over
                    >
                    <v-card
                        v-for="object in searchResults"
                        :key="object.id"
                        class="pa-2 justify-center"
                        align="center" 
                        justify="center"
                        outlined>
                        <div>
                            <a v-bind:href="object.detail_url" target="_blank">
                            <p>{{ object.title }}</p>
                            <img v-bind:src="object.image_url.replace('resolution=superImageResolution', 'resolution=mediumImageResolution')" height="200" >
                            </a>
                        </div>   
                    </v-card>
                </v-card>
            </v-col>    
        </v-row>
        </div>
    </v-container>
</template>

<script>
import { mapGetters } from 'vuex';
import Spinner from '@/components/Spinner.vue';

export default {
    props: {
        searchResults: {
            type: Array,
            required: true
        }
    },
    data() {
        return {
        }
    },
    components:{
        Spinner
    },
    computed: {
        ...mapGetters(['getIsLoading'])
    }

}
</script>

<style lang="css" scoped>
.results-wrapper {
  overflow-y: auto;
  height: 60vh;
  display: flex;
  flex-flow: column;
  align-items: center;
  margin: 10px;
  padding: 4px;
}
</style>