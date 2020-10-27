<template>
  <div>
    <h1>Reverse Image Search ETH Collection</h1>
    <div>
      <DragAndDrop/>
      <!-- <img src="https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=4083&resolution=lowImageResolution" height="200" > -->
      <!-- <hr style="height:5px;border-width:0;color:black;background-color:black"> -->
    </div>

  </div>
</template>

<script>
import DragAndDrop from '@/components/DragAndDrop.vue';

  export default {
    data() {
      return {
        info:null,
        loading: true,
        errored: false,
        objects: []

      }
    },
     mounted () {

    },
    components: {
      DragAndDrop
    }
  }
</script>

<style scoped>


</style>