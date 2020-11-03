import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
      fileSelected: false,
      uploadReady: false,
      resultsLoaded: false,
      searchResults: [
        {
          title:'Hero Alpen Rosti',
          image_url:'https://www.coop.ch/img/produkte/310_310/RGB/3030912_001.jpg?_=1581397360696',
          detail_url:'https://www.coop.ch/en/food/inventories/staples/potato-products/roesti-gratin/hero-alpen-roesti/p/3030912?context=search',
        },
        {
          title:'Rosti',
          image_url:'https://www.coop.ch/img/produkte/310_310/RGB/3030287_001.jpg?_=1585892809498',
          detail_url:'https://www.coop.ch/en/food/inventories/staples/potato-products/roesti-gratin/roesti/p/3030287?context=search',
        },
        {
          image_url:'https://www.coop.ch/img/produkte/310_310/RGB/3032754_001.jpg?_=1581491914876',
          detail_url:'https://www.coop.ch/en/food/inventories/staples/potato-products/roesti-gratin/naturaplan-organic-ready-to-eat-roesti/p/3032754?context=search',        
          title: "Naturaplan Organic Ready To Eat Rösti"
        },
        {
          title:'Hero Alpen Rosti',
          image_url:'https://www.coop.ch/img/produkte/310_310/RGB/3030912_001.jpg?_=1581397360696',
          detail_url:'https://www.coop.ch/en/food/inventories/staples/potato-products/roesti-gratin/hero-alpen-roesti/p/3030912?context=search',
        },
        {
          title:'Rosti',
          image_url:'https://www.coop.ch/img/produkte/310_310/RGB/3030287_001.jpg?_=1585892809498',
          detail_url:'https://www.coop.ch/en/food/inventories/staples/potato-products/roesti-gratin/roesti/p/3030287?context=search',
        },
        {
          image_url:'https://www.coop.ch/img/produkte/310_310/RGB/3032754_001.jpg?_=1581491914876',
          detail_url:'https://www.coop.ch/en/food/inventories/staples/potato-products/roesti-gratin/naturaplan-organic-ready-to-eat-roesti/p/3032754?context=search',        
          title: "Naturaplan Organic Ready To Eat Rösti"
        },
      ]
  },
  mutations: {
    CHANGE_UPLOAD_STATUS(state, status) {
      state.uploadReady = status
    },
    CHANGE_FILESELECTED_STATUS(state, status) {
      state.fileSelected = status
    }
  },
  actions: {
    changeUploadStatus( { commit }, status) {
      commit('CHANGE_FILESELECTED_STATUS', status)
    }
  },
  getters: {
    isFileSelected(state) {
      return state.fileSelected
    },
    getSearchResults(state) {
      return state.searchResults
    },
    getUploadStatus: state => {
      return state.uploadReady
    },
    resultsLoaded(state) {
      return state.searchResults.length >0
    }
  },
  modules: {
  }
})
