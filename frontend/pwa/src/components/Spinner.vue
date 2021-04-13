<template>
  <div>
      <v-row
        justify="center"
        align="center">
          <v-progress-circular
            indeterminate
            color="primary"
          />
      </v-row>
      <v-row
        justify="center"
        align="center">
        <p>
          {{message}}
        </p>
      </v-row>
    </div>
</template>

<script>
  export default {
    props:{
      message: {
        type: String,
        required: false,
        default: '...loading'
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>