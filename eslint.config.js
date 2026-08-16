export default [
    {
        ignores: [
            'node_modules/**',
            '.venv/**',
            'venv/**',
            '__pycache__/**',
            '.git/**',
            '.ruff_cache/**',
            'data/tests/input/**',
            'data/tests/output/**'
        ]
    },
    {
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module'
        },
        rules: {
            'no-unused-vars': 'error',
            'prefer-const': 'error',
            'no-var': 'error',
            eqeqeq: 'error',
            curly: 'error'
        }
    }
];
