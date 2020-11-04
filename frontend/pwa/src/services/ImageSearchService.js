import axios from 'axios'

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: false,
    headers: {
        'Content-Type': 'multipart/form-data'
    }
})

export default {
    uploadImage(selectedImage) {
        let formData = new FormData()
        formData.append('image', selectedImage)
        console.log('in upload service:', selectedImage)
        for (var key of formData.entries()) {
            console.log(key[0] + ', ' + key[1]);
        }
    
        let headers = { headers: {
                'Content-Type': 'multipart/form-data'
                }
            }
        return apiClient.post('image-search', formData, headers)
    }
}