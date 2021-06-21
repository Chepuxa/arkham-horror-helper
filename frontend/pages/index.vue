<template>
    <v-row justify="center" align="center">
        <v-col cols="12" md="9">
            <keep-alive>
                <Chat :room="0" />
            </keep-alive>
        </v-col>
    </v-row>
</template>

<script>
import Chat from '~/components/Chat.vue'

export default {
    components: {
        Chat,
    },
    middleware: 'authenticated'
}
</script>
