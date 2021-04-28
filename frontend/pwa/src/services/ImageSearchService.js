import axios from 'axios'

const apiClient = axios.create({
    // Vue sends requests from the user's browser so the api url must be publicly accessible, not just name spaced in docker-compose 
    baseURL: process.env.VUE_APP_API_BASE_URL, //load from env file
    withCredentials: false,
    headers: {
        'Content-Type': 'multipart/form-data'
    },
    timeout:10000,

})

export default {
    uploadImage(selectedImage) {
        let formData = new FormData()
        formData.append('image', selectedImage)    
        let headers = { headers: {
                'Content-Type': 'multipart/form-data'
                }
            }
        return apiClient.post('image-search', formData, headers)
    },
    saveSearchResults(searchResultID) {
        let formData = new FormData()
        formData.append('id', searchResultID)
        formData.append('keep', true)
        let headers = { headers: {
                'Content-Type': 'multipart/form-data'
                }
            }
        return apiClient.post(`save-search-result`, formData, headers)
    }
}