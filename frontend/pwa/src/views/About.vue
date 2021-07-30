<template>
  <div>
    <v-container class="my-0 py-0" >
      <v-row class="mt-0 pt-0" align="center" justify="center">
        <v-col 
          class="mt-0 pt-0" 
          xs="12" 
          sm="11" 
          md="10" 
          lg="8" 
          align="center">

          <v-img src="../assets/grs-title-small.gif" max-width="500px" />
          

            <!-- <h1>open imageSearch</h1>
            <h3 class="font-weight-light mb-6">- AI for art collections -</h3> -->
        </v-col>
        <v-col 
          class="mt-0 pt-0" 
          xs="12" 
          sm="11" 
          md="8" 
          lg="6" 
          align="center">
            <h2>About</h2>
            <p align="left">
              Developed as a collaboration between 
              <a target="_" href="https://www.librarylab.ethz.ch/">ETH Library Lab</a> 
              and 
              <a target="_" href="https://gs.ethz.ch">Graphische Sammlung ETH Zürich</a> ,
              <strong>open imageSearch</strong> seeks to improve the efficiency of cataloguing and digitising 
              print graphics by improving access to publicly available image metadata.
              It is an image retrieval, or reverse image search, application designed for art collections.
            </p>
            <p>
                <emphasis>Uses include:</emphasis><br/>
                
                - identifying unknown works<br/>
                - finding related works in a series<br/>
                - reducing time for data entry<br/>
                - art history research<br/>
                - checking for duplicated records
                
            </p>
            <h2>How It Works</h2>
            <p align="left">
              Uploaded images are sent to a Convolutional Neural Network which calculates 
              identifying features such as textures, shapes and color. These are compared 
              to the records in our database to find the most similar 
              images and a list of the top results are displayed. A summary 
              of the key information about the work can be previewed in the app. Links to 
              the image provider's website allow more detailed information to be seen.
            </p>
            <p>
              <v-img 
                class="my-2" 
                src="../assets/GraphischeSammlung-ReverseImageSearch-20210420_4_small.gif" 
                max-width="500px" />
            </p>
            <h2>Contact</h2>
            <p class="mb-2" align="left">
              If you are interested in the project, or would like to join the network of 
              collections participating in this project we would love to hear from you.
              Please see our github page or the contact us through our parent sites:<br/>
            </p>
            <p class="ma-0">
              <a
              class="no-underline" 
              href="https://github.com/eth-library-lab/open-image-search" target="_blank">
              <v-icon large>mdi-github</v-icon>
                <span class="underline-on-hover text-h6">open-image-search</span>
              </a>
            </p>
            <p class="ma-0 pa-0">
              <v-btn
                class="ma-1 mx-4"
                icon
                :height="height+10"
                :width="height+40"
                >
                <GSLogo 
                  color="black" 
                  :size="height +25"
                  link="https://gs.ethz.ch/en/contact/"
                  title="contact Graphische Sammlung"/>
              </v-btn>
              <v-btn
                class="ma-1 mx-4"
                icon
                :height="height+10"
                :width="height+30"
                >
                <LibLabLogo
                  color="black"
                  :size="height+25"
                  link="https://www.librarylab.ethz.ch/contact/"
                  title="contact ETH Library Lab"/>
              </v-btn>
            </p>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import GSLogo from '@/components/GSLogo.vue';
import LibLabLogo from '@/components/LibLabLogo.vue';
    export default {
      components: {GSLogo, LibLabLogo},
      computed: {
        height() {
          switch (this.$vuetify.breakpoint.name) {
            case 'xs': return 75
            case 'sm': return 85
            case 'md': return 90
            case 'lg': return 95
            case 'xl': return 95
          } return 100
        }
      }   
    }
</script>

<style lang="css" scoped>

.no-underline {
  text-decoration:none; 
}

.underline-on-hover:hover {
  text-decoration: underline;
}
</style>