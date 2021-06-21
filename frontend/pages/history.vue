<template>
    <v-row justify="center" align="center">
        <v-col cols="12" md="9">
            <v-card 
                v-for="room in sortedHistory"
                :key="room.id"
                elevation="4"
                class="my-4 pa-4"
            >
                <div class="result-main">
                    <div class="result-summary my-2">
                        <h2>
                            Игра от {{ (new Date(room.start_date * 1000)).toLocaleString('ru-RU') }} (создал {{ room.room_author }}) &mdash;
                            <span v-if="room.victory" style="color: #66bb6a;">победа</span>
                            <span v-else style="color: #f44336;">поражение</span>
                        </h2>
                    </div>
                    <div class="result-columns my-2">
                        <div class="result-characters mr-2">
                            <p>
                                Древний:&nbsp;
                                <span style="font-weight: bold;">
                                    {{ room.ancient }}
                                </span>
                            </p>
                            <p
                                v-for="char in room.characters"
                                :key="char.name"
                            >
                                <span style="font-weight: bold;">
                                    {{ char.name }}
                                </span>
                                <span v-if="char.health.value === 0">
                                    погиб(-ла).
                                </span>
                                <span v-else-if="char.mental.value === 0">
                                    сошёл (сошла) с ума.
                                </span>
                                <span v-else>
                                    остаётся с {{ char.health.value }} здоровья и {{ char.mental.value }} рассудка.
                                </span>
                            </p>
                        </div>
                        <div class="result-metrics">
                            <p>
                                Безысходность: {{ room.despair.value }} / {{ room.despair.highest }}
                            </p>
                            <p>
                                Порталы: {{ room.portals.value }} / {{ room.portals.highest }}
                            </p>
                            <p>
                                Ужас: {{ room.terror.value }} / {{ room.terror.highest }}
                            </p>
                            <p>
                                Окраины: {{ room.outskirts.value }} / {{ room.outskirts.highest }}
                            </p>
                            <p>
                                Монстры:
                            </p>
                            <monster-list v-if="room.monsters.length > 0" :disabled="true" :limit="room.monster_cap" :monsters="room.monsters" />
                            <p v-else>
                                нет
                            </p>
                        </div>
                    </div>
                    <div class="action-log my-2">
                        <h3>Лог действий</h3>
                        <div v-for="action in room.action_log" :key="action.date">
                            <p class="author">
                                {{ action.user }}
                            </p>
                            <p class="text">
                                {{ action.text }}
                            </p>
                        </div>
                    </div>
                </div>
            </v-card>
        </v-col>
    </v-row>
</template>

<script>
import MonsterList from '@/components/MonsterList.vue'

export default {
    components: { MonsterList },
    middleware: 'authenticated',
    asyncData({ $axios }) {
        return $axios.$get(`/room/complete`).then((response) => {
            return {
                history: response
            }
        })
    },
    data() {
        return {}
    },
    computed: {
        sortedHistory() {
            const sorted = this.history.slice()
            sorted.sort((left, right) => { return left.start_date - right.start_date })

            for (const room of sorted) {
                room.action_log.sort((left, right) => { return left.date - right.date })
            }
            return sorted
        }
    },
    methods: {}
}
</script>

<style>

.result-main {
    display: flex;
    flex-direction: column;
}

.result-columns {
    display: flex;
    flex-direction: row;
}

.result-characters {
    width: 50%;
}

.action-log {
    overflow-y: auto;
    overflow-x: auto;
    max-height: 200px;
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

.action-log p {
    margin-bottom: 8px;
}

</style>