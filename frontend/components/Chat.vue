<template>
    <v-sheet elevation="4" shaped>
        <div class="chat-box">
            <div ref="messageBox" class="message-box">
                <div v-for="message in messages" :key="message.date" class="message">
                    <p class="author">
                        {{ message.user }}
                    </p>
                    <p class="text">
                        {{ message.text || message.message }}
                    </p>
                </div>
            </div>
            <v-form ref="chat" class="input" @submit.prevent="submitMessage">
                <v-text-field
                    v-model="current_message"
                    append-icon="mdi-send"
                    dense
                    outlined
                    label="Введите сообщение..."
                    @click:append="submitMessage"
                />
            </v-form>
        </div>
    </v-sheet>
</template>

<script>
export default {
    name: 'Chat',
    props: {
        room: {
            required: true,
            type: Number,
        },
    },
    data() {
        return {
            current_message: '',
            messages: [],
            ws: null,
            ready: false,
            nickname: null
        }
    },
    created() {
        const wsBaseURL = this.$config.baseURL.replace(/http/, 'ws')
        const url = wsBaseURL + '/wsapi' + ((this.room === 0) ? `/chat/ws` : `/room/{room}/ws`)

        this.ws = new WebSocket(url)
        this.ws.onopen = this.handleWebsocketReady
        this.ws.onmessage = this.handleWebsocketMessage

        this.nickname = this.$cookies.get('nickname').value

        this.fetchHistory()
    },
    methods: {
        addSystemMessage(text) {
            this.messages.push({
                date: Date.now() / 1000,
                user: 'Система',
                text
            })
            this.scrollChat()
        },
        scrollChat() {
            const el = this.$refs.messageBox
            if (el) {
                this.$nextTick(() => {
                    el.scrollTop = el.scrollHeight
                })
                // el.scrollIntoView(false) // only works on children
            }
        },
        handleWebsocketReady() {
            this.ready = true
            this.addSystemMessage('Вы подключены к чату!')
        },
        handleWebsocketMessage(raw_message) {
            const message = JSON.parse(raw_message.data)
            this.messages.push(message)
            this.scrollChat()
        },
        handleWebsocketClosed() {
            this.ready = false
        },
        submitMessage() {
            if (this.ready) {
                const raw_message = JSON.stringify({
                    user: this.nickname,
                    text: this.current_message
                })
                this.ws.send(raw_message)
                this.current_message = ''
            }
        },
        fetchHistory() {
            const url = ((this.room === 0) ? `/chat/history` : `/room/{room}/history`)
            this.$axios.$get(url).then((response) => {
                const messages = response.slice()
                messages.sort((left, right) => { return left.date - right.date })
                this.messages.unshift(...messages)
                this.scrollChat()
            }).catch((error) => {
                this.addSystemMessage('Не удалось загрузить историю сообщений.')
            })
        }
    }
}
</script>

<style>
.chat-box {
    /* background-color: var(--v-secondary-base); */
    padding: 16px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: space-between;

    height: 80vh;
}

.chat-box > .message-box {
    background-color: var(--v-accent-darken2);
    border: 1px solid var(--v-accent-base);
    margin-bottom: 24px;

    padding: 8px;
    border-radius: 8px;

    flex-grow: 1;

    font-size: 90%;

    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    /* overflow-x: hidden; */
    overflow-y: scroll;
}

.chat-box > .input {
    flex-grow: 0;
}

.chat-box > .message-box > .message {
    display: inline-flex;
    flex-direction: row;
    align-items: baseline;
    justify-content: flex-start;
}

.chat-box .message > p {
    margin-bottom: 8px;
}

.chat-box .message > .author {
    font-weight: bold;
    margin-right: 0.75em;
}

.chat-box .message > .text {
    overflow-wrap: anywhere;
}
</style>
