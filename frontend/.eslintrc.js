module.exports = {
    root: true,
    env: {
        browser: true,
        node: true
    },
    parserOptions: {
        parser: 'babel-eslint'
    },
    extends: [
        '@nuxtjs',
        'plugin:nuxt/recommended'
    ],
    plugins: [
    ],
    // add your custom rules here
    rules: {
        'indent': ['warn', 4],
        'vue/html-indent': ['warn', 4],
        'space-before-function-paren': ['error', 'never'],
        'comma-dangle': [
            'warn',
            "only-multiline"
        ],
        'quotes': [
            'warn',
            'single',
            {
                'allowTemplateLiterals': true
            }
        ],
        'eol-last': ['warn', "always"],
        'semi': ['warn', "never"],
        'camelcase': "off",
        'no-trailing-spaces': 'warn',
        'spaced-comment': 'warn',
        'no-multi-spaces': 'warn',
        'no-multiple-empty-lines': 'warn',
        'prefer-const': 'warn',
        'no-unused-vars': 'warn',
        'node/handle-callback-err': 'warn',
        'quote-props': 'warn'
    }
}
