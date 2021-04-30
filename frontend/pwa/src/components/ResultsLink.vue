<template>
<div>
    <v-row>
        <v-col
            xs="9" 
            sm="9" 
            md="9" 
            lg="9"
            class="ma-0 px-1"
            >
            <v-text-field 
                v-model="this.resultsUrl"
                readonly
                class="results-link text-caption my-0 py-1" 
                ref="resultsLinkRef">
                {{ this.resultsUrl }}
            </v-text-field>
        </v-col>
        <v-col
            class="ma-0"
            xs="3" 
            sm="3" 
            md="3" 
            lg="3"
            ><v-btn
                small
                :disabled="copySnackbar"
                color="primary"
                @click="copyUrlTwice"
                class="text-caption py-4"
                >
                {{ copySnackbar ? "copied" : "copy" }}
            </v-btn>
        </v-col>
    </v-row>
</div>
</template>

<script>
export default {
    props:{ 
        resultsUrl: {
            type: Array,
            required: true
        }
    },
    data: () => ({ 
        copySnackbar: false
    }),
    methods:{
        copyUrlTwice() {
        // temp workaround
        // if there is already text in the clipboard, 
        //the copy command needs to be repeated to 
        // overwrite the existing clipboard content
        this.copyUrl()
        this.copyUrl()
            this.copySnackbar = true      
        setTimeout(() => {  
            this.copySnackbar = false
            }, 1200)
        },
        copyUrl() {
            // Select the inviteLink text
            var resultsLink = document.querySelector('.results-link')
            var range = document.createRange()
            range.selectNode(resultsLink)
            window.getSelection().addRange(range)
            try {
                // Now that we've selected the text, execute the copy command
                var successful = document.execCommand('copy')
            } catch(err) {
                console.log('clipboard error: unable to copy');
            }
            window.getSelection().removeAllRanges()
        }
    }
}
</script>

<style lang="scss" scoped>
</style>