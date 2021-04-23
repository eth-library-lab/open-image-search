import Vue from 'vue'
import Vuex from 'vuex'

import ImageSearchService from '@/services/ImageSearchService.js';
const { version } = require('../../package.json');
Vue.use(Vuex)

export default new Vuex.Store({
  state: {
      appVersion: version,
      fileSelected: false,
      selectedFile: null,
      uploadReady: false,
      resultsLoaded: false,
      isLoading: false,
      searchResults: [],
      searchResultId: null,
      snackbar: {
        visible: false,
        timeout:10000,
        text: "an error occured",
        multiline: false,
      }
  },
  mutations: {
    CHANGE_UPLOAD_STATUS(state, status) {
      state.uploadReady = status
    },
    CHANGE_FILESELECTED_STATUS(state, status) {
      state.fileSelected = status
    },
    CHANGE_RESULTSLOADED_STATUS(state, status) {
      state.resultsLoaded = status
    },
    CHANGE_ISLOADING_STATUS(state, status) {
      state.isLoading = status
    },
    SET_SEARCH_RESULTS(state, searchResults) {
      state.searchResults = searchResults
    },
    SET_SEARCH_RESULT_ID(state, results_id) {
      state.searchResultId = results_id
    },
    UPDATE_SELECTED_FILE(state, file) {
      state.selectedFile = file
    },
    SHOW_SNACKBAR(state, payload) {
      state.snackbar.visible = true
      state.snackbar.timeout = payload.timeout
      state.snackbar.text = payload.text
      state.snackbar.multiline = payload.multiline
    },
    CLOSE_SNACKBAR(state) {
      state.snackbar.visible = false
      state.snackbar.multiline = false
      state.snackbar.timeout = 3000
      state.snackbar.text = null
    },
  },
  actions: {
    changeFileSelectedStatus( { commit }, status) {
      commit('CHANGE_FILESELECTED_STATUS', status)
    },
    changeResultsLoadedStatus( { commit }, status) {
      commit('CHANGE_RESULTSLOADED_STATUS', status)
    },
    changeIsLoadingStatus( { commit }, status) {
      commit('CHANGE_ISLOADING_STATUS', status)
    },
    searchSimilarImages({ commit, dispatch }, selectedImage) {
      // console.log('in searchSimilarImages selectedImage', selectedImage)
      ImageSearchService.uploadImage(selectedImage)
        .then(response => {
          // console.log("searchSimilarImages, response.data:", response.data)
          commit('SET_SEARCH_RESULTS', response.data.results)
          commit('SET_SEARCH_RESULT_ID',response.data.result_id)
          dispatch('changeResultsLoadedStatus', true)
        })
        .catch(error => {
          console.log("in searchSimilarImages error: ", error)
          console.log("axios error.code:", error.code)
          this.errored = true
          if (error.code == "ECONNABORTED") {
            dispatch('showSnackbar', 'Request timed out. Please try again')
            console.log("Request timed out. Please try again")
          } else {
            console.log('error: ', error)
            var snackbarSettings = {
                text:'Encountered error with search service. \n Please try again or let us know if this is a recurring issue',
                timeout:-1
            }
            dispatch('showSnackbar',snackbarSettings)
            
          }
        })
        .finally(() => {
          dispatch('changeIsLoadingStatus',false)
        })
    },
    showSnackbar({ commit }, {text, timeout} ) {
      let snackbarSettings = {
        visible: true,
        timeout:3000,
        text:"error occured",
        multiline: false
      }
      snackbarSettings.text = text
      if (text) {
        snackbarSettings.multiline = (text.length > 50) ? true : false
      }
      
      if (timeout) {
        snackbarSettings.timeout = timeout
      }
      commit('SHOW_SNACKBAR', snackbarSettings)
    },
    closeSnackbar( {commit,} ) {
      commit('CLOSE_SNACKBAR')
    }
  },
  getters: {
    appVersion(state) {
      return state.appVersion
    },
    isFileSelected(state) {
      return state.fileSelected
    },
    getSearchResults(state) {
      return state.searchResults
    },
    resultsLoaded(state) {
      return state.resultsLoaded
    },
    getIsLoading(state) {
      return state.isLoading
    },
    snackbarState(state) {
      return state.snackbar
    }

  },
  modules: {
  }
})
