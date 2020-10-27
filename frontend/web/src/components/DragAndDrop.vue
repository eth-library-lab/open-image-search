<template>
    <div style="text-align: center;">
        <div :class="[isUploadDisabled ?  'upload-box' : 'upload-box uploadReady']" 
            id="app" 
            @click="clickFileInput"
            v-cloak 
            @drop.prevent="addFile"
            @dragover.prevent>
        <h2>Upload a Search Image</h2>
        <div v-show="!this.selectedImage">
            <h5><i>Click or Drag and Drop</i></h5>
            <input type="file" 
                style="display: none;" 
                ref="fileInput"
                @change="onInputFileSelected">
        </div>
        <table v-if="this.selectedImage"
            class="table table-hover">
            <thead>
                <tr>
                    <th>thumbnail</th>
                    <th>file name</th>
                    <th>size</th>
                    <th>remove</th>
                </tr>
            </thead>
            <tbody>
                <tr v-if="selectedImage" :key="selectedImage.id">
                    <td :id="'gallery-'+selectedImage.name"></td>
                    <td>
                        <p>{{ selectedImage.name }}</p> 
                    </td>
                    <td>{{ kb_filter(selectedImage.size) }} kb</td>
                    <td>
                        <button class="remove-button" 
                            @click="removeFile()" 
                            title="Remove File"
                            v-on:click.stop>X</button>
                    </td>
                </tr>
            </tbody>
        </table>
        <div id="gallery"></div>
        </div>
        <button v-if="!isUploadDisabled" class="btn-search" 
            :disabled="isUploadDisabled" 
            @click="upload"
            :title="[isUploadDisabled ? 'need to add files first' : 'click to upload']"
            >Search</button>
        <div>searchResults: {{ searchResults }} </div>
    
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data() {
        return {
            selectedImage: null,
            uploadDisabled: true,
            searchResults: []
        }
    },
    computed: {
        isUploadDisabled() {
            return this.selectedImage == null
        }
    },
    methods:{
        clickFileInput() {
            if (this.isUploadDisabled) {
                this.$refs.fileInput.click()
            }
        },
        previewFile(file) {
            let reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onloadend = function() {
                let img = document.createElement('img')
                img.src = reader.result
                img.height = 100
                img.id='img-'+file.name
                document.getElementById('gallery-'+file.name).appendChild(img)
            }
        },
        kb_filter(val) {
            return Math.floor(val/1024).toLocaleString('en');  
        },
        addFile(e) {
            let droppedFiles = e.dataTransfer.files;
            if(!droppedFiles) return;
            // this tip, convert FileList to array, credit: https://www.smashingmagazine.com/2018/01/drag-drop-file-uploader-vanilla-js/
            this.selectedImage = droppedFiles[0];
        },
        onInputFileSelected(event) {
            let newFile = event.target.files[0]

            if (newFile) {
                this.selectedImage = newFile
                this.previewFile(newFile)
            }
        },
        removeFile(){
            this.selectedImage = null
        },
        upload() {
            
            let formData = new FormData()
            formData.append('image', this.selectedImage)

            console.log(formData.keys)
            let searchURL = '//localhost:8000/image-search'
            let headers = { headers: {
                    'Content-Type': 'multipart/form-data'
                    }
                }
            axios
                .post(searchURL, formData, headers)
                .then(response => {
                    console.log(response)
                    this.searchResults = response.data
                    })
                .catch(error => {
                console.log(error)
                this.errored = true
                })
                .finally(() => this.loading = false)
            
        }
    }
}
</script>

<style scoped>
.table{
    margin-right: auto;
    margin-left: auto;
    border-collapse: separate;
    border-spacing: 50px 0;
}
.td{
    padding: 50px 0;
}
.upload-box{
    margin: auto;
    border: 5px solid #5C7D8A;
    background: #76a0b11a;
    border-radius: 15px;
    max-width:750px;
    transition: all 1s;
    
}
.upload-box:hover{
    background: #98cee47c;
}
.uploadDisabled{
    background:rgba(61, 58, 58, 0.205);
}
.uploadReady{
    background: #98cee4e3;
    transition: all 1s;
}
.uploadReady:hover{
    background:#98cee4e3;
}
.btn-search{
    margin:10px;
    padding:15px;
    font-size: 1.3em;
    font-weight: bold;
    border-radius: 15px;
    background-color:#98cee4e3;
}
.remove-button{
    padding:5px;
    background-color:black;
    z-index: 5;
}
</style>