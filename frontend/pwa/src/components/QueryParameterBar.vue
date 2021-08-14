<template>
    <div>
        <v-expansion-panels flat>
          <v-expansion-panel
          flat
            >
            <v-expansion-panel-header>
               Additional Query Parameters
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-row
                align="center" justify="center">
              <v-col
                align="center" justify="center"
                class="px-4 mx-12"
                >
                <span class="v-label theme--light mb-0 px-0">
                  year filter
                </span>
                <v-range-slider
                  v-model="range"
                  :disabled="selectionsDisabled"
                  :max="max"
                  :min="min"
                  hide-details
                  class="align-center"
                >
                <template v-slot:thumb-label="props">
                    {{props.value}}
                </template>
                  <template v-slot:prepend>
                    <v-text-field
                      :value="range[0]"
                      class="mt-0 pt-0"
                      hide-details
                      single-line
                      type="number"
                      style="width: 60px"
                      @change="$set(range, 0, $event)"
                    ></v-text-field>
                  </template>
                  <template v-slot:append>
                    <v-text-field
                      :value="range[1]"
                      class="mt-0 pt-0"
                      hide-details
                      single-line
                      type="number"
                      style="width: 60px"
                      @change="$set(range, 1, $event)"
                    ></v-text-field>
                  </template>
                </v-range-slider>
                <v-select
                  v-model="materialTechnique"
                  :disabled="selectionsDisabled"
                  :items="materialTechniques"
                  label="Material or Technique"
                ></v-select>
                <v-select
                  v-model="classification"
                  :disabled="selectionsDisabled"
                  :items="classifications"
                  label="Classification"
                ></v-select>
                <v-select
                  v-model="collection"
                  :items="collections"
                  :disabled="true | selectionsDisabled"
                  label="collection"
                ></v-select>
              </v-col>
            </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
  </div>
</template>

<script>
    export default {
      data() {
        return {
          selectionsDisabled:false,
          min: 1400,
          max: 2021,
          range: [1400, 2021],
          classification:null,
          materialTechnique:null,
          classifications:['Print', 'Book', 'Plate', 'Hand Drawing'],
          materialTechniques:["lithographie", "radierung", "kupferstich"],
          collections:["ETHZ Graphische Sammlung"]
        }
      }
    }
</script>

<style lang="css" scoped>

</style>