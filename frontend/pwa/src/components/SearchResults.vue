<template>
    <v-container>
        <div >
        <v-row justify="center">
            <h3>Search Results</h3>
        </v-row>
        <v-row>
            <v-card
                class="d-flex align-content-start flex-wrap"
                color="grey lighten-2"
                flat
                >
                <v-card
                    v-for="object in objects"
                    :key="object.id"
                    class="pa-2"
                    outlined>
                    <div>
                        <a v-bind:href="object.detail_url" target="_blank">
                        <p>{{ object.title }}</p>
                        <img v-bind:src="object.image_url.replace('resolution=superImageResolution', 'resolution=mediumImageResolution')" height="200" >
                        </a>
                    </div>   
                </v-card>
            </v-card>
        </v-row>

        </div>
    </v-container>
</template>

<script>
export default {
    props: {
        searchResults: {
            type: Array,
            required: true
        }
    }
}
</script>

<style lang="css" scoped>
.results-wrapper {
  overflow-y: scroll;
  height: 60vh;
  display: flex;
  flex-flow: column;
  align-items: center;
  margin: 10px;
  padding: 4px;
}
</style>