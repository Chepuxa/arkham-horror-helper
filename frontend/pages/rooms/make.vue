<template>
    <v-row justify="center" align="start">
        <v-col class="pa-2" cols="12" md="6">
            <v-card class="pa-4 my-4" elevation="4">
                <h2>Сыщики</h2>
                <template v-for="name in names">
                    <v-checkbox
                        :key="name"
                        v-model="selectedNames"
                        class="mx-1 my-2 pa-1"
                        :label="name"
                        :value="name"
                    />
                </template>
            </v-card>
        </v-col>
        <v-col class="pa-2" cols="12" md="6">
            <v-card class="pa-4 my-4" elevation="4">
                <h2>Древние</h2>
                <v-radio-group v-model="chosenAncient">
                    <v-radio
                        v-for="ancient in ancients"
                        :key="ancient.name"
                        class="mx-1 my-2 pa-1"
                        :label="`${ancient.name} (${ancient.value})`"
                        :value="ancient"
                    />
                </v-radio-group>
            </v-card>
            <v-card class="pa-4 my-4" elevation="4">
                <v-btn
                    block
                    elevation="2"
                    color="primary"
                    :loading="loading"
                    @click="create"
                >
                    Создать комнату
                </v-btn>
                <v-alert
                    v-if="!!alertText"
                    elevation="8"
                    type="error"
                    class="mt-2"
                >
                    {{ alertText }}
                </v-alert>
            </v-card>
        </v-col>
    </v-row>
</template>

<script>
export default {
    middleware: 'authenticated',
    data() {
        return {
            names: [
                'Аманда Шарп',
                'Боб Дженкинс',
                'Винсент Ли',
                'Глория Голдберг',
                'Даррел Симонс',
                'Декстер Дрейк',
                'Дженни Барнс',
                'Джо Даймонд',
            ],
            ancients: [
                {
                    name: 'Итаква',
                    value: 11,
                },
                {
                    name: 'Ктулху',
                    value: 13,
                },
                {
                    name: 'Азатот',
                    value: 14,
                },
            ],
            selectedNames: [],
            chosenAncient: null,
            loading: false,
            alertText: null
        }
    },
    methods: {
        create() {
            const nickname = this.$cookies.get('nickname').value

            if (!!this.chosenAncient && (this.selectedNames.length > 0)) {
                this.alertText = null

                const payload = {
                    author: nickname,
                    ancient: this.chosenAncient.name,
                    despair_limit: this.chosenAncient.value,
                    characters: []
                }

                for (const character of this.selectedNames) {
                    payload.characters.push({
                        name: character,
                        health: 5,
                        mental: 5
                    })
                }

                this.loading = true
                this.$axios.$post('/room/make', payload).then((response) => {
                    const room_data = response
                    const room_id = room_data.id
                    this.$router.push({
                        path: `/rooms/${room_id}`
                    })
                }).catch((error) => {
                    this.alertText = error.toString()
                }).finally(() => {
                    this.loading = false
                })
            } else {
                this.alertText = 'Выберите древнего и хотя бы одного сыщика'
                return
            }

            setTimeout(() => {
                this.loading = false
            }, 1000)
        }
    }
}
</script>
