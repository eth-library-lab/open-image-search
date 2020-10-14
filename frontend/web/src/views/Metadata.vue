<template>
  <div>
    <h1>This is a page of MetaData</h1>

    <div v-for="object in objects" v-bind:key="object.id">
      <hr>
      <div>
        <a v-bind:href="object.detail_url">{{ object.title }}</a>
      </div>
      <div>
        <img v-bind:src="object.image_url" height="200">
      </div>
    </div>  
  </div>
</template>

<script>
import axios from 'axios'
// axios.defaults.baseURL = 'http://localhost:8000/';

  export default {
    data() {
      return {
        info:null,
        loading: true,
        errord: false,
        objects: []
        //   {
        //     "id": 1000,
        //     "object_id": 3,
        //     "created_date": "2020-10-14T11:00:32Z",
        //     "title": "Marcus Curtius stürzt sich in die Erdspalte",
        //     "image_url": "https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=3&resolution=superImageResolution",
        //     "detail_url": "https://www.graphikportal.org/document/gpo00215594?medium=A3FA20B1",
        //     "detail_description": "Monogrammist IB [Nagler III 1950] (Erwähnt um 1523 - 1530), Künstler, 1529"
        // },
        // {
        //     "id": 1001,
        //     "object_id": 18,
        //     "created_date": "2020-10-14T11:00:32Z",
        //     "title": "Die Philister bringen die Bundeslade in den Tempel von Dagan",
        //     "image_url": "https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=18&resolution=superImageResolution",
        //     "detail_url": "https://www.graphikportal.org/document/gpo00215592?medium=C4DF20E7",
        //     "detail_description": "Battista Franco (Um 1510 - 1561), Um 1525 - 1561"
        // },
        // {
        //     "id": 1002,
        //     "object_id": 19,
        //     "created_date": "2020-10-14T11:00:32Z",
        //     "title": "Der grosse Saal im Schloss in Prag [Linke Bildhälfte]",
        //     "image_url": "https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=19&resolution=superImageResolution",
        //     "detail_url": "https://www.graphikportal.org/document/gpo00214855?medium=C4E020E8",
        //     "detail_description": "Egidius Sadeler (der Jüngere) (Um 1570 - 1629), Ausführung, 1607, Marcus Christoph Sadeler (1614 - ?; erwähnt 1660), Herausgeber"
        // },
        // {
        //     "id": 1003,
        //     "object_id": 33,
        //     "created_date": "2020-10-14T11:00:32Z",
        //     "title": "Die schöne Försterin",
        //     "image_url": "https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=33&resolution=superImageResolution",
        //     "detail_url": "https://www.graphikportal.org/document/gpo00214860?medium=C4DE20E4",
        //     "detail_description": "Henry Wyatt (1794 - 1840), nach, 1835, Francis Graham Moon (1796 - 1871), Herausgeber"
        // },
        // {
        //     "id": 1004,
        //     "object_id": 52,
        //     "created_date": "2020-10-14T11:00:32Z",
        //     "title": "Stigmatisation des heiligen Franziskus",
        //     "image_url": "https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=52&resolution=superImageResolution",
        //     "detail_url": "https://www.graphikportal.org/document/gpo00214859?medium=C4E120E5",
        //     "detail_description": "Agostino Carracci (1557 - 1602), Ca. 1583"
        // },
        // ]    
      }
    },
     mounted () {


      axios
        .get('http://localhost:8000/image-metadata?limit=10/')
        .then(response => {
          this.objects = response.data['results']
        })
        .catch(error => {
          console.log(error)
          this.errored = true
        })
        .finally(() => this.loading = false)
    }
  }
</script>

<style scoped>

</style>