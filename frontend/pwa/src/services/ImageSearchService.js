import axios from 'axios'

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: false,
    headers: {
        'Content-Type': 'multipart/form-data'

    }
})

export default {
    uploadImage() {
        let formData = new FormData()
        formData.append('image', this.selectedImage)

        console.log(formData.keys)
        let headers = { headers: {
                'Content-Type': 'multipart/form-data'
                }
            }
        this.isLoading = true
        apiClient
            .post('image-search', formData, headers)
            .then(response => {
                console.log(response)
                return response.data
                })
            .catch(error => {
            console.log(error)
            this.errored = true
            })
            .finally(() => this.isLoading = false)
        
    }
}