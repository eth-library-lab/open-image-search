<template>
    <div>
      <div>
        <!-- {{this.filterOptions}} -->
        filterOptionsLoaded: {{this.filterOptionsLoaded}}
        filterOptions: {{Object.keys(this.filterOptions)}}
        materialTechniques: {{materialTechniques}}
      </div>

        <v-expansion-panels flat>
          <v-expansion-panel
          flat
            >
            <v-expansion-panel-header
              @click="loadFilterOptions"
              >
               Additional Query Parameters
            </v-expansion-panel-header>
            <v-expansion-panel-content
              >
              <v-row
                align="center" justify="center"
                v-if="filterOptionsLoaded"
                >
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
                <v-combobox
                  v-model="materialTechnique"
                  :disabled="selectionsDisabled"
                  :items="materialTechniques"
                  multiple
                  label="Material or Technique"
                ></v-combobox>
                <v-combobox
                  v-model="classification"
                  :disabled="selectionsDisabled"
                  :items="classifications"
                  multiple
                  label="Classification"
                ></v-combobox>
                <v-combobox
                  v-model="collection"
                  :items="collections"
                  :disabled="selectionsDisabled"
                  multiple
                  label="collection"
                ></v-combobox>
              </v-col>
            </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {

  data() {
    return {
      selectionsDisabled:false,
      min: 1400,
      max: 2021,
      range: [1400, 2021],
      classification:null,
      materialTechnique:null,
      collection:null,
    }
  },
  computed: {
    ...mapGetters(['filterOptions','filterOptionsLoaded']),
    materialTechniques() {
      if (this.filterOptionsLoaded) {
        // let options = []
        // this.filterOptions.materialTechniques.forEach(el => 
        //   options.push(el.name)
        // )
        // return options
        return this.filterOptions.materialTechniques
      } else {
        return []
      }
    },
    classifications() {
      if (this.filterOptionsLoaded) {
        return this.filterForName('classifications')
      } else {
        return []
      }
    },
    institutions() {
      if (this.filterOptionsLoaded) {
        return this.filterForName('institutions')
      } else {
        return []
      }
    },
  },
  methods: {
    ...mapActions(['getFilterOptions']),
    loadFilterOptions() {
      console.log('loadFilterOptions ', this.loadFilterOptions)
      if (!this.filterOptionsLoaded) {
        console.log('this.getFilterOptions()')
        this.getFilterOptions()
        console.log(this.filterOptions)
        console.log("this.optionsLoaded: ",this.filterOptionsLoaded)
      }
    },
    filterForName(keyName) {
        let options = []
        this.filterOptions[keyName].forEach(el => 
          options.push(el.name)
        )
        return options
      // } else {
        // return []
      // }
    }
  },
  mounted() {
  }
}
</script>

<style lang="css" scoped>

</style>