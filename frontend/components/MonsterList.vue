<template>
    <v-card 
        elevation="8"
        class="monster-list-outer"
    >
        <div v-if="!disabled" class="tip">
            Чтобы удалить монстра, нажмите на него
        </div>
        <div class="monster-list-wrapper">
            <div class="monster-list">
                <v-btn
                    v-for="(monster, index) in monsters"
                    :key="index"
                    fab
                    dark
                    x-small
                    color="primary"
                    class="ma-1"
                    :disabled="disabled"
                    @click="handleRemoval(monster)"
                >
                    <v-icon dark>
                        {{ `${icons[monster]}` }}
                    </v-icon>
                </v-btn>
            </div>
            <div class="spacer" />
            <div class="monster-limit ml-2">
                /&nbsp;{{ limit }}
            </div>
            <v-menu offset-y :class="{ 'hidden': disabled }">
                <template #activator="{ on, attrs }">
                    <v-btn
                        elevation="2"
                        :disabled="monsters.length >= limit || disabled"
                        class="monster-add-button ml-2"
                        :class="{ 'hidden': disabled }"
                        v-bind="attrs"
                        v-on="on"
                    >
                        <v-icon dark>
                            mdi-plus
                        </v-icon>
                    </v-btn>
                </template>
                <v-list>
                    <v-list-item
                        v-for="(icon, index) in icons"
                        :key="index"
                        @click="handleAddition(icon)"
                    >
                        <v-list-item-title>
                            <v-icon>
                                {{ icon }}
                            </v-icon>
                        </v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>
        </div>
    </v-card>
</template>

<script>
export default {
    name: 'MonsterList',
    props: {
        monsters: {
            type: Array,
            required: true
        },
        limit: {
            type: Number,
            required: true
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false
        }
    },
    data() {
        return {
            icons: {
                1: 'mdi-square',
                2: 'mdi-triangle',
                3: 'mdi-hexagon'
            }
        }
    },
    computed: {

    },
    methods: {
        handleAddition(icon) {
            let type = 0
            for (let i = 1; i <= 3; i += 1) {
                if (this.icons[i] === icon) { type = i }
            }
            this.$emit('new', type)
        },
        handleRemoval(type) {
            this.$emit('remove', type)
        },
    }
}
</script>

<style>

.monster-list-outer {
    display: flex;
    flex-direction: column;
    align-items: stretch;
}

.monster-list-outer > .tip {
    font-size: 60%;
}

.monster-list-wrapper {
    display: flex;
    flex-direction: row;
    align-items: center;
}

.monster-list {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
}

.monster-list-wrapper > .spacer {
    flex-grow: 1;
}

.hidden {
    display: none;
}

</style>
