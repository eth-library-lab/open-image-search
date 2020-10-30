<template>
    <div>
      <v-container>
       <v-row align="center" justify="center">
        <v-col cols="10" align="center">
            <v-card >
                <v-card-text class="font-weight-bold">Search Image</v-card-text>
                <div class="img-preview-container image-border" id="img-preview-container">
                <v-img 
                    v-if="selectedFile" 
                    :src="selectedFileSrc"
                    contain>
                </v-img>
                </div>
                <v-file-input
                v-model="selectedFile"
                show-size
                accept="image/png, image/jpeg, image/bmp"
                placeholder="Select a File"
                prepend-icon="mdi-image"
                @change="previewFile(selectedFile)"
            ></v-file-input>
            </v-card>
            </v-col>
        </v-row>
        </v-container>
    </div>
</template>

<script>
export default {
    data: () => ({
      selectedFile: null,
    }),
    methods: {
        removeExistingPreview() {
            var existingElement = document.getElementById('img-preview')
            if (existingElement) {
            existingElement.remove()
            }
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
        },
    }
}
</script>

<style lang="css" scoped>
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