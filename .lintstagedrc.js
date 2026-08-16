
export default {
    '*.py': ['ruff check --fix --unsafe-fixes --quiet --force-exclude', 'ruff format --quiet --force-exclude'],
    '*.go': './scripts/format-go-staged.sh',
    '*.{js,jsx,ts,tsx}': [
        'oxlint --fix --quiet --no-error-on-unmatched-pattern',
        'eslint --cache --cache-location .eslintcache --fix --quiet',
        'prettier --cache --write --log-level warn'
    ],
    '*.svelte': [
        'eslint --cache --cache-location .eslintcache --fix --quiet',
        'prettier --cache --write --log-level warn'
    ],
    'package.json': ['sort-package-json', 'prettier --cache --write --log-level warn'],
    '*.toml': ['taplo format'],
    '*.{json,md,yml,yaml,css,scss}': ['prettier --cache --write --log-level warn'],
    '*.sh': ['shfmt -w']
};
