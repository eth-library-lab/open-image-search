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
    numPossibleResults:null,
    filterOptions: {},
    filterOptionsLoading:false,
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
    SET_SEARCH_RESULTS(state, {searchResults, searchResultId, numPossibleResults}) {
      state.searchResults = searchResults
      state.searchResultId = searchResultId
      state.numPossibleResults = numPossibleResults
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
    UPDATE_FILTER_OPTIONS(state, filterOptions) {
      state.filterOptions = filterOptions
    },
    CHANGE_FILTERS_LOADING_STATUS(state, filterStatus) {
      state.filterOptionsLoading = filterStatus
    }
  },
  actions: {
    changeSearchResultId( { commit }, searchResultId) {
      commit('SET_SEARCH_RESULT_ID', searchResultId)
    },
    changeFileSelectedStatus( { commit }, status) {
      commit('CHANGE_FILESELECTED_STATUS', status)
    },
    changeResultsLoadedStatus( { commit }, status) {
      commit('CHANGE_RESULTSLOADED_STATUS', status)
    },
    changeIsLoadingStatus( { commit }, status) {
      commit('CHANGE_ISLOADING_STATUS', status)
    },
    changefiltersLoadingStatus( { commit }, status) {
      commit('CHANGE_FILTERS_LOADING_STATUS', status)
    },
    searchSimilarImages({ commit, dispatch }, payload) {
    
      var selectedImage = payload.selectedImage
      var queryString = payload.queryString
      ImageSearchService.uploadImage(selectedImage, queryString)
        .then(response => {
          const searchResults = response.data.results
          const searchResultId = response.data.resultId
          const numPossibleResults = response.data.numPossibleResults
          console.log("numPossibleResults: ",numPossibleResults)
          const payload = {searchResults, searchResultId, numPossibleResults}
          commit('SET_SEARCH_RESULTS', payload)
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
    saveSearchResults({dispatch, getters }, ) {
      
      ImageSearchService.saveSearchResults(getters.searchResultId)
        .then(() => {
          
        })
        .catch(error => {
          console.log("in saveSearchResults, error: ", error)
          console.log("axios error.code:", error.code)
          this.errored = true
          if (error.code == "ECONNABORTED") {
            dispatch('showSnackbar', 'Request timed out. Please try again')
            console.log("Request timed out. Please try again")
          } else {
            console.log('error: ', error)
            var snackbarSettings = {
                text:'Encountered error with api service. \n Please try again or let us know if this is a recurring issue',
                timeout:-1
            }
            dispatch('showSnackbar',snackbarSettings)
            
          }
        })
        .finally(() => {

        })
    },
    loadSearchResults({ commit, dispatch }, searchResultId) {
      ImageSearchService.getSearchResults(searchResultId)
        .then(response => {
          // get url for the original search image
          commit('UPDATE_SELECTED_FILE', response.data.image)
          const searchResults = response.data.results
          const searchResultId = searchResultId
          const payload = {searchResults, searchResultId}
          commit('SET_SEARCH_RESULTS', payload)
          dispatch('changeResultsLoadedStatus', true)
        })
        .catch(error => {
          console.log("loadSearchResults error: ", error.response )
          console.log("axios error.code:", error.code)
          this.errored = true
          // generic error message
          var snackbarSettings = {
            text:'Encountered error with search service. \n Please try again or let us know if this is a recurring issue',
            timeout:-1
          }
          if (error.code == "ECONNABORTED") {
            snackbarSettings.text='Request timed out. Please try again'
            console.log(snackbarSettings.text)
            dispatch('showSnackbar', snackbarSettings)
          } else if (error.response.status == 404 ) {
            snackbarSettings.text ='No search results were found this url. Please check the link and try again.'
            dispatch('showSnackbar', snackbarSettings)
            console.log('404: ', snackbarSettings.text)
          } else {
            console.log('error: ', error)
            dispatch('showSnackbar',snackbarSettings)
          }
        })
        .finally(() => {
          dispatch('changeIsLoadingStatus',false)
        })
    },
    getFilterOptions({ commit, dispatch }) {
      dispatch('changefiltersLoadingStatus', true)
      ImageSearchService.getFilterOptions()
        .then(response => {
          // get url for the original search image
          commit('UPDATE_FILTER_OPTIONS', response.data)
        })
        .catch(error => {
          console.log("getFilterOptions error: ", error.response )
          console.log("axios error.code:", error.code)
          this.errored = true
          // generic error message
          var snackbarSettings = {
            text:'Encountered error with filtered service. \n Please try again or try searching with less restrictive filters',
            timeout:-1
          }
          if (error.code == "ECONNABORTED") {
            snackbarSettings.text='Request timed out. Please try again'
            console.log(snackbarSettings.text)
            dispatch('showSnackbar', snackbarSettings)
          } else {
            console.log('error: ', error)
            dispatch('showSnackbar',snackbarSettings)
          }
        })
        .finally(() => {
          dispatch('changefiltersLoadingStatus', false)
        })
    },
    clearSearchResults({ commit }) {
      let payload = { 
        searchResults: [],
        searchResultId: null,
      }
      commit('SET_SEARCH_RESULTS', payload),
      commit('CHANGE_RESULTSLOADED_STATUS', false)
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
    getSelectedFile(state){
      return state.selectedFile
    },
    getSearchResults(state) {
      return state.searchResults
    },
    getNumPossibleResults(state){
      return state.numPossibleResults
    },
    resultsLoaded(state) {
      return state.resultsLoaded
    },
    getIsLoading(state) {
      return state.isLoading
    },
    snackbarState(state) {
      return state.snackbar
    },
    searchResultId(state) {
      return state.searchResultId
    },
    filterOptions(state) {
      return state.filterOptions
    },
    filterOptionsLoaded(state) {
      return Object.keys(state.filterOptions).length > 0
    }

  },
  modules: {
  }
})
