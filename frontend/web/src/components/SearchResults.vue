<template>
    <div>
        <div >
        <h3>Search Results</h3>
        <div class="results-wrapper" v-if="!loading" >
            
            <div class="result-card" v-for="object in searchResults" v-bind:key="object.id">
                <div>
                    <a v-bind:href="object.detail_url" target="_blank">
                    <p>{{ object.title }}</p>
                    <img v-bind:src="object.image_url.replace('resolution=superImageResolution', 'resolution=mediumImageResolution')" height="200" >
                    </a>
                </div>        
                <hr>
            </div>

        </div>
        </div>
    </div>
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