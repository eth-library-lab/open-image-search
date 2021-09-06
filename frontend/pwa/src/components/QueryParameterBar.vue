<template>
    <div>
      <div>
        <!-- {{this.filterOptions}} -->
        <!-- <p>
        filterOptionsLoaded: {{this.filterOptionsLoaded}}
        </p>
        <p>
          queryString: {{this.queryString}}
        </p> -->
        <!-- <p>
        materialTechnique: {{materialTechnique}}
        </p>
        <p>
        classification: {{classification}}
        </p>
        yearBefore: {{this.yearMax}}
        </p> 
        <p>
        yearAfter: {{yearMin}}
        </p>
        <p>
          institution: {{institution}}
        </p> -->
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
                    @change="emitQueryString"
                    :disabled="selectionsDisabled"
                    :max="2020"
                    :min="1400"
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
                    v-model="relationship"
                    @change="emitQueryString"
                    :disabled="selectionsDisabled"
                    :items="relationships"
                    multiple
                    label="relationship to other works"
                  ></v-combobox>
                  <v-combobox
                    v-model="classification"
                    @change="emitQueryString"
                    :disabled="selectionsDisabled"
                    :items="classifications"
                    multiple
                    label="Classification"
                  ></v-combobox>
                  <v-combobox
                    v-model="materialTechnique"
                    @change="emitQueryString"
                    :disabled="selectionsDisabled"
                    :items="materialTechniques"
                    multiple
                    label="Material or Technique"
                  ></v-combobox>
                  <v-combobox
                    v-model="institution"
                    @change="emitQueryString"
                    :items="institutions"
                    :disabled="selectionsDisabled"
                    multiple
                    label="institution"
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
      yearMin:1400,
      yearMax:2020,
      range: [null,null],
      classification:null,
      relationship:null,
      materialTechnique:null,
      institution:null,
    }
  },
  computed: {
    ...mapGetters(['filterOptions','filterOptionsLoaded']),
    materialTechniques() {
      if (this.filterOptionsLoaded) {
        let options = []
        this.filterOptions.materialTechniques.forEach(el => 
          options.push(el.name)
        )
        return options
      } else {
        return []
      }
    },
    relationships() {
      if (this.filterOptionsLoaded) {
        let options = []
        this.filterOptions.relationships.forEach(el => 
          options.push(el.name)
        )
        return options
      } else {
        return []
      }
    },
    classifications() {
      if (this.filterOptionsLoaded) {
        let options = []
        this.filterOptions.classifications.forEach(el => 
          options.push(el.name)
        )
        return options
      } else {
        return []
      }
    },
    institutions() {
      if (this.filterOptionsLoaded) {
        let options = []
        this.filterOptions.institutions.forEach(el => 
          options.push(el.name)
        )
        return options
      } else {
        return []
      }
    },
    queryString() {
      let queryString="?"

      if (this.range[0]!=null){
        let afterYearQuery=`afterYear=${this.range[0]}`
        queryString = queryString + "&" + afterYearQuery
        let beforeYearQuery=`beforeYear=${this.range[1]}`
        queryString = queryString + "&" + beforeYearQuery

      }

      if (this.classification) {
        let queryParam=""
        this.classification.forEach(el => {
          queryParam = queryParam + `&classification=${el}`
        })
        queryString = queryString + queryParam
      }
      if (this.materialTechnique) {
        let queryParam=""
        this.materialTechnique.forEach(el => {
          queryParam = queryParam + `&materialTechnique=${el}`
        })
        queryString = queryString + queryParam
      }
      if (this.relationship) {
        let queryParam=""
        this.relationship.forEach(el => {
          queryParam = queryParam + `&relationship=${el}`
        })
        queryString = queryString + queryParam
      }
      if (this.institution) {
        let institutionQuery=`institution=${this.institution}`
        queryString = queryString + institutionQuery
      }
      if (queryString.length > 1) {
        return queryString
      } else {
        return ""
      }
    }

  },
  methods: {
    ...mapActions(['getFilterOptions']),
    async loadFilterOptions() {
      console.log('loadFilterOptions ', this.loadFilterOptions)
      if (!this.filterOptionsLoaded) {
        console.log('this.getFilterOptions()')
        this.getFilterOptions()
        this.yearMin = await this.filterOptions.yearMin
        this.yearMax = await this.filterOptions.yearMax
        this.range = await [this.filterOptions.yearMin, this.filterOptions.yearMax]
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
    },
    emitQueryString() {
      this.$emit('query-string', this.queryString)
    },
  },
  mounted() {
  }
}
</script>

<style lang="css" scoped>

</style>