<template>
    <v-row justify="center" align="center">
        <v-col cols="12" md="9">
            <div>
                <v-form ref="form" class="form" @submit.prevent="submitNickname">
                    <v-text-field
                        v-model="nickname"
                        append-icon="mdi-send"
                        dense
                        outlined
                        label="Ваш никнейм"
                        @click:append="submitNickname"
                    />
                    <v-btn
                        elevation="4"
                        @click="submitNickname"
                    >
                        Представиться
                    </v-btn>
                </v-form>
            </div>
        </v-col>
    </v-row>
</template>

<script>
import Chat from '~/components/Chat.vue'

export default {
    data() {
        return {
            nickname: ''
        }
    },
    methods: {
        submitNickname() {
            if (this.nickname) {
                this.$cookies.set(
                    'nickname',
                    { value: this.nickname },
                    {
                        maxAge: 60 * 60 * 24 * 365,
                        sameSite: 'Strict',
                        
                    }
                )
                this.$router.push({
                    path: '/'
                })
            }
        }
    }
}
</script>
