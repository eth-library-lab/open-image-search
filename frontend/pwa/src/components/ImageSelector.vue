<template>
    <div>
        <v-container v-if="!isFileSelected" class='mt-2'>
            <v-col class='tight' align="center">
                <p class='tight' >search the graphics collection of ETH Zurich for similar images</p>
            </v-col>
        </v-container>
      <v-container class="my-0 py-0">
       <v-row class="mt-0 pt-0" align="center" justify="center">
        <v-col class="mt-0 pt-0" xs="12" sm="11" md="10" lg="10" align="center">
            <v-card >
                <v-card-text class="font-weight-bold my-1 pb-1">Search Image</v-card-text>
                <v-row align="center" justify="center">
                    <v-col 
                        v-show="isFileSelected" 
                        align="center" 
                        justify="center">
                        <div 
                            class="img-preview-container image-border" 
                            id="img-preview-container">
                        </div>
                    </v-col>
                    <v-col class="ma-0 py-0"
                        align-self="end">
                        <v-file-input 
                            class="ma-0 py-0"
                            v-model="selectedFile"            
                            show-size
                            accept="image/png, image/jpeg, image/bmp"
                            placeholder="Select a File"
                            prepend-icon="mdi-image"
                            @change="previewFile(selectedFile)"
                            @click:clear="clearResults()"
                        ></v-file-input>
                    </v-col>
                </v-row>
                <!-- <v-row >
                    <v-col justify="center" v-if="resultsLoaded" class="ma-0 pa-0">
                        <v-icon
                            @click="clearResults()"
                            class="pa-4"
                            title="clear results and search image">
                            mdi-close-box
                        </v-icon>
                    </v-col>
                </v-row> -->
                </v-card>
            </v-col>
        </v-row>
        <v-row v-if="isFileSelected & !resultsLoaded" 
            align="center"
            justify="center">
            <v-col cols="10" align="center">
            <v-btn 
                class="align-center"
                color="primary"
                elevation="2"
                @click="uploadImage">
                Upload
            </v-btn>
            </v-col>
        </v-row>
    </v-container>
    </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
    data: () => ({
      selectedFile: null,
    }),
    computed: {
        ...mapGetters(['resultsLoaded', 'isFileSelected']),
    },
    methods: {
        ...mapActions(['changeFileSelectedStatus','changeResultsLoadedStatus']),
        removeExistingPreview() {
            var existingElement = document.getElementById('img-preview')
            if (existingElement) {
            existingElement.remove()
            }
            this.changeFileSelectedStatus(false)
        },
        uploadImage() {
            this.changeFileSelectedStatus(true)
            this.changeResultsLoadedStatus(true)
        },
        previewFile(imageFile) {
            this.removeExistingPreview()
            let reader = new FileReader()
            reader.readAsDataURL(imageFile)
            reader.onloadend = function() {
                let img = document.createElement('img')
                img.src = reader.result
                img.class='img-preview'
                img.id='img-preview'
                img.style="max-height:30vh; max-width:75vw"
                img.display='flex'
                document.getElementById('img-preview-container').appendChild(img)
            }
            this.changeFileSelectedStatus(true)
        },
        clearResults() {
            this.selectedFile = null
            this.removeExistingPreview()
            this.changeResultsLoadedStatus(false)
            this.changeFileSelectedStatus(false)
        }
    }
}
</script>

<style lang="css" scoped>

.tight {
  padding:3px;
  padding-top:3px;
  margin-bottom:3px;
}
.v-file-input{
  width: 95%;
  padding-left: 50px;
  padding-right: 50px;
}
.img-preview-container{
  min-height: 0vh;
  max-height: 55vh;
}
.image-border{
  border: black;
  border-width: 10px;
}
.img-preview{
    height: 50px;
    display: flex;
}
.circle {
    width: 100px;
    height: 100px;
    background: red;
    -moz-border-radius: 50px;
    -webkit-border-radius: 50px;
    border-radius: 50px;
}
</style>