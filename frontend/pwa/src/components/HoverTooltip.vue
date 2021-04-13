<template>
<div>
  <v-tooltip
    right
    max-width="350px"
    open-delay="750"
    color='primary'
    >
    <template #activator="data">
      <div v-on="data.on" v-bind="data.attrs"
        >
        <slot ></slot>
      </div>
    </template>
    <div>
      <h3>{{object.title}}</h3>
      <p>{{object.person}}</p>
      <p class="my-0">{{object.date}}</p>
      <p>{{object.material_technique}}</p>
      <p class="my-0">{{object.institution_isil}}</p>
      <p class="my-0"><i>InventarNummer</i>: {{" " + object.inventory_number}}</p>
      <p class="my-0"><i>Lizenz</i>:  {{" " + object.image_licence}}</p>
    </div>
  </v-tooltip>

</div>
</template>

<script>
export default {
  props: ['object']
}
</script>

<style lang="scss" scoped>

</style>