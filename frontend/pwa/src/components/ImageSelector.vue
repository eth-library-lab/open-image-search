<template>
    <div>
        <v-container v-if="!isFileSelected" class='mt-2'>
            <v-col class='tight' align="center">
                <p class='tight' >search the graphics collection of ETH Zurich for similar images</p>
            </v-col>
        </v-container>
      <v-container class="my-0 py-0">
       <v-row align="center" justify="center">
        <v-col class="mt-0 pt-0" xs="12" sm="11" md="10" lg="10" align="center">
            <v-card  >
                <v-card-text class="font-weight-bold">Search Image</v-card-text>
                <v-row>
                <v-col>
                    <v-file-input
                        v-model="selectedFile"
                        v-if="resultsLoaded"                    
                        show-size
                        accept="image/png, image/jpeg, image/bmp"
                        placeholder="Select a File"
                        prepend-icon="mdi-image"
                        @change="previewFile(selectedFile)"
                ></v-file-input>
                </v-col>
                <v-col v-if="selectedFile" justify="end">
                    <div class="img-preview-container image-border" id="img-preview-container">
                    <v-img 
                        v-if="selectedFile" 
                        :src="selectedFileSrc"
                        contain>
                    </v-img>
                    </div>
                </v-col>
                </v-row>
                </v-card>
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
        ...mapGetters(['resultsLoaded']),
        isFileSelected() {
            return this.$store.getters.isFileSelected
        },
    },
    methods: {
        ...mapActions(['changeUploadStatus']),
        removeExistingPreview() {
            var existingElement = document.getElementById('img-preview')
            if (existingElement) {
            existingElement.remove()
            }
            this.changeUploadStatus(false)
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

            this.changeUploadStatus(true)
        },
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
</style>