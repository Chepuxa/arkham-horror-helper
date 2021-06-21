<template>
    <v-row justify="center" align="start">
        <v-col v-if="!!room" cols="12" sm="6" md="4">
            <v-card
                v-for="(character, index) in room.characters"
                :key="character.name"
                class="counter-grid pa-4 my-4"
            >
                <div class="counter-long">
                    {{ character.name }}
                </div>
                <div class="counter-label">
                    <v-icon
                        color="red darken-2"
                    >
                        mdi-heart
                    </v-icon>
                    Здоровье:
                </div>
                <counter
                    :value="character.health.value"
                    :lowest="character.health.lowest"
                    :highest="character.health.highest"
                    :disabled="!canMakeMoves"
                    @increase="makeChange('+', `character ${index} health`)"
                    @decrease="makeChange('-', `character ${index} health`)"
                />
                <div class="counter-label">
                    <v-icon
                        color="yellow darken-2"
                    >
                        mdi-brain
                    </v-icon>
                    Рассудок:
                </div>
                <counter
                    :value="character.mental.value"
                    :lowest="character.mental.lowest"
                    :highest="character.mental.highest"
                    :disabled="!canMakeMoves"
                    @increase="makeChange('+', `character ${index} mental`)"
                    @decrease="makeChange('-', `character ${index} mental`)"
                />
            </v-card>
        </v-col>
        <v-col v-if="!!room" cols="12" sm="6" md="4">
            <v-card class="counter-grid pa-4 my-4">
                <div class="counter-label">
                    Древний:
                </div>
                <div class="counter-text-value">
                    {{ room.ancient }}
                </div>
                <div class="counter-label">
                    Безысходность:
                </div>
                <counter
                    :value="room.despair.value"
                    :lowest="room.despair.lowest"
                    :highest="room.despair.highest"
                    :disabled="!canMakeMoves"
                    @increase="makeChange('+', 'despair')"
                    @decrease="makeChange('-', 'despair')"
                />
                <div class="counter-label">
                    Порталы:
                </div>
                <counter
                    :value="room.portals.value"
                    :lowest="room.portals.lowest"
                    :highest="room.portals.highest"
                    :disabled="!canMakeMoves"
                    @increase="makeChange('+', 'portals')"
                    @decrease="makeChange('-', 'portals')"
                />
                <div class="counter-label">
                    Ужас:
                </div>
                <counter
                    :value="room.terror.value"
                    :lowest="room.terror.lowest"
                    :highest="room.terror.highest"
                    :disabled="!canMakeMoves"
                    @increase="makeChange('+', 'terror')"
                    @decrease="makeChange('-', 'terror')"
                />
            </v-card>

            <v-card class="counter-grid pa-4 my-4">
                <monster-list
                    :monsters="room.monsters"
                    :limit="room.monster_cap"
                    class="counter-long"
                    :disabled="!canMakeMoves"
                    @new="handleMonsterAdded"
                    @remove="handleMonsterRemoved"
                />
                <div class="counter-label">
                    Окраины:
                </div>
                <counter
                    :value="room.outskirts.value"
                    :lowest="room.outskirts.lowest"
                    :highest="room.outskirts.highest"
                    :disabled="!canMakeMoves"
                    @increase="makeChange('+', 'outskirts')"
                    @decrease="makeChange('-', 'outskirts')"
                />
            </v-card>
        </v-col>
        <v-col v-if="!!room" cols="12" sm="6" md="4">
            <v-card class="pa-4 my-4">
                <v-btn
                    elevation="4"
                    block
                    class="my-2"
                    color="primary"
                    :disabled="!canMakeMoves"
                    @click="confirmGameOver(true)"
                >
                    Завершить игру победой
                </v-btn>
                <v-btn
                    elevation="4"
                    block
                    class="my-2"
                    color="error darker-2"
                    :disabled="!canMakeMoves"
                    @click="confirmGameOver(false)"
                >
                    Завершить игру поражением
                </v-btn>
            </v-card>
            <v-card class="action-log pa-4 my-4">
                <div v-for="action in sortedLog" :key="action.date">
                    <p class="author">
                        {{ action.user }}
                    </p>
                    <p class="text">
                        {{ action.text }}
                    </p>
                </div>
            </v-card>
        </v-col>
    </v-row>
</template>

<script>
import Counter from '@/components/Counter.vue'
import MonsterList from '@/components/MonsterList.vue'

export default {
    components: { Counter, MonsterList },
    middleware: 'authenticated',
    asyncData: ({ $axios, params }) => {
        return $axios.$get(`/room/${params.id}`).then((response) => {
            return {
                room: response
            }
        })
    },
    data() {
        return {
            loading: false,
            nickname: null,
            room_id: this.$route.params.id,
            ws: null,
            ws_ready: false,
        }
    },
    computed: {
        sortedLog() {
            if (!this.room) { return [] }
            const log = this.room.action_log.slice()
            log.sort((left, right) => { return right.date - left.date })
            return log
        },
        canMakeMoves() {
            return (!this.room.complete)
        }
    },
    created() {
        const wsBaseURL = this.$config.baseURL.replace(/http/, 'ws')
        const url = wsBaseURL + `/wsapi/room/${this.room_id}/ws`

        this.nickname = this.$cookies.get('nickname').value
        this.ws = new WebSocket(url)
        this.ws.onopen = this.handleWebsocketReady
        this.ws.onmessage = this.handleWebsocketMessage
    },
    methods: {
        handleMonsterAdded(type) {
            this.makeChange('new', 'monsters', { type })
        },
        handleMonsterRemoved(type) {
            this.makeChange('remove', 'monsters', { type })
        },
        handleWebsocketReady() {
            this.ws_ready = true
        },
        handleWebsocketMessage(raw_message) {
            const room_object = JSON.parse(raw_message.data)
            this.room = room_object
        },
        makeChange(what, where, extra) {
            const change = {
                who: this.nickname,
                what,
                where,
                extra
            }
            /* this.$axios.$post(`/room/${this.room_id}`, change).then((response) => {
                if (response) {
                    this.room = response
                } else {
                    alert('no change!')
                }
            }) */
            this.ws.send(JSON.stringify(change))
        },
        confirmGameOver(victory) {
            const outcome = victory ? 'победой' : 'поражением'
            const confirmed = confirm(`Вы действительно хотите закончить эту игру ${outcome}?`)
            if (confirmed) {
                this.makeChange(victory ? '+' : '-', 'victory')
            }
        }
    }
}
</script>

<style>

.counter-grid {
    display: grid;
    grid-template-columns: auto auto;
    justify-items: stretch;
    align-items: center;

    gap: 8px;
}

.counter-label {
    justify-self: end;
}

.counter-long {
    grid-column: 1 / span 2;
    font-weight: bold;
}

.counter-row {
    display: flex;
    flex-direction: row;
    align-items: center;
}

.action-log {
    overflow-y: auto;
    overflow-x: auto;
    max-height: 600px;
}

.action-log > div {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
}

.action-log .author {
    font-weight: bold;
    margin-right: 8px;
}

</style>
