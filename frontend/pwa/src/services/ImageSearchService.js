import axios from 'axios'
import { mapActions } from 'vuex'

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: false,
    headers: {
        'Content-Type': 'multipart/form-data'

    }
})

export default {
    ...mapActions(['changeResultsLoadedStatus', 'changeIsLoadingStatus']),
    uploadImage() {
        let formData = new FormData()
        formData.append('image', this.selectedImage)
        console.log(formData.keys)
        let headers = { headers: {
                'Content-Type': 'multipart/form-data'
                }
            }
        this.changeIsLoadingStatus(true)
        apiClient
            .post('image-search', formData, headers)
            .then(response => {
                console.log(response)
                this.changeResultsLoadedStatus(true)
                return response.data
                })
            .catch(error => {
            console.log(error)
            this.errored = true
            })
            .finally(() => this.changeIsLoadingStatus(false))
        
    }
}