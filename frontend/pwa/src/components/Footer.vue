<template>
    <v-footer fixed padless >
        <v-card flat tile class="flex">
            <v-row class="text-center">
                <v-col>
                <p>
                    <br />
                    developed by
                </p>
                <LibLabLogo color="black" size="125"/>
                </v-col>
            </v-row>
        </v-card>
    </v-footer>
</template>

<script>
import LibLabLogo from '@/components/LibLabLogo.vue';

export default {
    components:{
        LibLabLogo
    }
    
}
</script>

<style lang="scss" scoped>

</style>