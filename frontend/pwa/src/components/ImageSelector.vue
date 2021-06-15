<template>
    <div>
        <v-container v-if="!isFileSelected" class='mt-2'>
            <v-col 
                class='tight' 
                align="center">
                <p class='tight' >
                    search the Graphics Collection of ETH Zurich for similar images
                </p>
            </v-col>
        </v-container>
      <v-container class="my-0 py-0" >
        <v-form
            v-model="valid"
            >
            <v-row class="mt-0 pt-0" align="center" justify="center">
                <v-col 
                    class="mt-0 pt-0" 
                    xs="12" 
                    sm="11" 
                    md="10" 
                    lg="8" 
                    align="center">
                    <v-card >
                        <v-card-text 
                            class="font-weight-bold my-1 pb-1"
                            >
                            Search Image
                        </v-card-text>
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
                                    v-model="selectedFile"
                                    :rules="fileInputRules"
                                    class="ma-0 py-0"
                                    show-size
                                    accept="image/png, image/jpeg, image/jpg, image/bmp, image/tiff, image/tif"
                                    placeholder="Select a File"
                                    prepend-icon="mdi-image"
                                    color="primary"
                                    @change="previewAndSelectFile(selectedFile)"
                                    @click:clear="clearResults()"
                                ></v-file-input>
                            </v-col>
                        </v-row>
                    </v-card>
                </v-col>
            </v-row>

            <v-row
                v-if="!(resultsLoaded | getIsLoading)"
                align="center"
                justify="center">
                <v-col cols="10" align="center">
                    <v-btn 
                        :disabled="!isFileSelected || !valid"
                        type="submit"
                        class="align-center"
                        color="primary"
                        elevation="2"
                        ref="uploadImageBtn"
                        :title="!isFileSelected ? 'no file selected':'ok'"
                        @click="uploadImage">
                        Upload
                    </v-btn>
                </v-col>
            </v-row>
        </v-form>
    </v-container>
    </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
    data: () => ({
        selectedFile: null,
        valid: true,
        fileInputRules: [
            value => !value || value.size < 10000000 || 'Image size should be less than 10 MB',
        ],
    }),
    computed: {
        ...mapGetters(['resultsLoaded', 'isFileSelected','getIsLoading']),
    },
    methods: {
        
        ...mapActions(['changeFileSelectedStatus',
                        'changeResultsLoadedStatus',
                        'searchSimilarImages',
                        'changeIsLoadingStatus']),
        removeExistingPreview() {
            var existingElement = document.getElementById('img-preview')
            if (existingElement) {  
            existingElement.remove()
            }
            this.changeFileSelectedStatus(false)
        },
        previewFile(imageFile) {
            
            let reader = new FileReader()

            reader.readAsDataURL(imageFile)
            
            if ( (imageFile.type == "image/tiff") || (imageFile.type == "image/tif") ) {
                reader.onloadend = function() {
                    let img = document.createElement('v-text')
                    img.src = reader.result
                    img.class='img-preview'
                    img.id='img-preview'
                    img.style="max-height:30vh; max-width:75vw; font-style: italic; font-size: 14px;"
                    img.display='flex'
                    img.innerHTML="<em>tiff file preview is not supported</em>"
                    document.getElementById('img-preview-container').appendChild(img)
                }
            } else {
                reader.onloadend = function() {
                    let img = document.createElement('img')
                    img.src = reader.result
                    img.class='img-preview'
                    img.id='img-preview'
                    img.style="max-height:30vh; max-width:75vw"
                    img.display='flex'
                    document.getElementById('img-preview-container').appendChild(img)
                }
            }
            this.changeFileSelectedStatus(true)
        },
        clearResults() {
            this.selectedFile = null
            this.removeExistingPreview()
            this.changeIsLoadingStatus(false)
            this.changeResultsLoadedStatus(false)
            this.changeFileSelectedStatus(false)
        },
        selectFile(imageFile){
            this.selectedFile = imageFile
        },
        previewAndSelectFile(imageFile){
            // remove previous files and preview
            this.clearResults()
            this.removeExistingPreview()
            //preview and set new file
            this.previewFile(imageFile)
            this.selectFile(imageFile)
            this.$refs.uploadImageBtn.$el.focus()
        },
        uploadImage() {
            this.changeIsLoadingStatus(true)
            this.searchSimilarImages(this.selectedFile)
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
.circle {
    width: 100px;
    height: 100px;
    background: red;
    -moz-border-radius: 50px;
    -webkit-border-radius: 50px;
    border-radius: 50px;
}
</style>