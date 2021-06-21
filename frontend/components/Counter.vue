<template>
    <div class="counter-wrapper">
        <v-btn
            elevation="2"
            :disabled="!canDecrease || disabled"
            @click="handleChange('-')"
        >
            <v-icon dark>
                mdi-minus
            </v-icon>
        </v-btn>
        <div class="number mx-2">
            {{ formattedValue }}
        </div>
        <v-btn
            elevation="2"
            :disabled="!canIncrease || disabled"
            @click="handleChange('+')"
        >
            <v-icon dark>
                mdi-plus
            </v-icon>
        </v-btn>
    </div>
</template>

<script>
export default {
    name: 'Counter',
    props: {
        value: {
            type: Number,
            required: true
        },
        lowest: {
            type: Number,
            required: true,
        },
        highest: {
            type: Number,
            required: true
        },
        showHighest: {
            type: Boolean,
            required: false,
            default: true
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false
        }
    },
    computed: {
        canIncrease() {
            return this.value < this.highest
        },
        canDecrease() {
            return this.value > this.lowest
        },
        formattedValue() {
            if (this.showHighest) {
                return `${this.value} / ${this.highest}`
            } else {
                return `${this.value}`
            }
        }
    },
    methods: {
        handleChange(type) {
            if (type === '+') {
                this.$emit('increase')
            } else if (type === '-') {
                this.$emit('decrease')
            }
        }
    }
}
</script>

<style>

.counter-wrapper {
    display: flex;
    flex-direction: row;
    align-items: center;
}

.counter-wrapper > .number {
    flex-grow: 1;

    display: flex;
    align-items: center;
    justify-content: center;
}

</style>
