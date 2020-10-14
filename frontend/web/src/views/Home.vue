<template>
  <div>
    <img alt="Logo" height="200" src="https://gs.ethz.ch/wp-content/uploads/2020/04/Franz-Gertsch_Banner__klein_4750_1371.gif" />
    <ReverseImageSearch msg="ETH Graphische Sammlung"/>
  </div>
</template>

<script>
// @ is an alias to /src
import ReverseImageSearch from "@/components/ReverseImageSearch.vue";

export default {
  name: "Home",
  components: {
    ReverseImageSearch
  }
};
</script>
