<template>
    <div style="text-align: center;">
        <div class="upload-box" 
            id="app" 
            @click="this.$refs.fileInput.click" 
            v-cloak 
            @drop.prevent="addFile" 
            @dragover.prevent>
        <h2>Upload a Search Image</h2>
        <h5><i>Click or Drag and Drop</i></h5>
        <input type="file" 
            style="display: none;" 
            ref="fileInput" 
            @change="onInputFileSelected">
        
        <ul>
            <li v-for="file in files" :key="file.id">
                {{ file.name }} ({{ kb_filter(file.size) }} bytes) 
                <button @click="removeFile(file)" title="Remove">X</button>
            </li>
        </ul>
        
        </div>
        <button v-if="!isUploadDisabled" :class="{ uploadDisabled: isUploadDisabled }"
            :disabled="isUploadDisabled" 
            @click="upload"
            :title="[isUploadDisabled ? 'need to add files first' : 'click to upload']"
            >Search</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            files:[],
            uploadDisabled: true,
        }
    },
    computed: {
        isUploadDisabled() {
            return this.files.length == 0 
        }
    },
    methods:{
        kb_filter(val) {
            return Math.floor(val/1024);  
        },
        addFile(e) {
        let droppedFiles = e.dataTransfer.files;
        if(!droppedFiles) return;
        // this tip, convert FileList to array, credit: https://www.smashingmagazine.com/2018/01/drag-drop-file-uploader-vanilla-js/
        ([...droppedFiles]).forEach(f => {
            this.files.push(f);
        });
        },
        onInputFileSelected(event) {
                this.files.push(event.target.files[0])
            },
        removeFile(file){
        this.files = this.files.filter(f => {
            return f != file;
        });      
        },
        upload() {
        
        let formData = new FormData();
        this.files.forEach((f,x) => {
            formData.append('file'+(x+1), f);
        });
        
        fetch('https://httpbin.org/post', {
            method:'POST',
            body: formData
        })
        .then(res => res.json())
        .then(res => {
            console.log('done uploading', res);
        })
        .catch(e => {
            console.error(JSON.stringify(e.message));
        });
        }
    }
}
</script>

<style scoped>
.upload-box{
    margin: auto;
    border: 5px solid #5C7D8A;
    background: #76a0b11a;
    border-radius: 10px;
    max-width:750px;
    
}
.upload-box:hover{
    background: #98cee45e;
}
.uploadDisabled{
    background:rgba(61, 58, 58, 0.205);
}
</style>