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
    uploadImage(selectedImage, queryString) {
        let formData = new FormData()
        formData.append('image', selectedImage)
        let headers = { headers: {
            'Content-Type': 'multipart/form-data'
            }
        }
        if (!queryString) {
            queryString= ''
        } 

        let url = 'image-search'
        url = url + queryString
        return apiClient.post(url, formData, headers)
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
    },
    getSearchResults(searchResultID) {
        return apiClient.get(`search-results/${searchResultID}`)
    },
    getFilterOptions() {
        return apiClient.get(`filter-options`)
    }
}