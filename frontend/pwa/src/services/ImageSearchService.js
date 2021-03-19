import axios from 'axios'

const apiClient = axios.create({
    // Vue sends requests from the user's browser so the api url must be publicly accessible, not just name spaced in docker-compose 
    baseURL: 'http://167.71.61.215:8000',
    withCredentials: false,
    headers: {
        'Content-Type': 'multipart/form-data'
    },
    timeout:5000,

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