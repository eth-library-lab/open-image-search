<template>
  <div>
    <img alt="Logo" height="200" src="https://gs.ethz.ch/wp-content/uploads/2020/04/Franz-Gertsch_Banner__klein_4750_1371.gif" />
    <h1>ETH Graphische Sammlung</h1>
    
    <GSLogo />
      <p>
        prototype tool to search the graphics collection of ETH Zurich by finding similar images 
      </p>
      <p>
        <br />
        developed by
      </p>
    <LibLabLogo color="black" size="125"/>
    <!-- <Spinner size="500"/> -->
  </div>
</template>

<script>
import GSLogo from '@/components/GSLogo.vue';
import LibLabLogo from '@/components/LibLabLogo.vue';

export default {
  name: "Home",
  components: {
    GSLogo,
    LibLabLogo
  }
};
</script>
