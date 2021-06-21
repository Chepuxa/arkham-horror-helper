export default function({ app, store, redirect }) {
    const cookie = app.$cookies.get('nickname')

    if (!cookie) {
        return redirect('/login')
    }
}
