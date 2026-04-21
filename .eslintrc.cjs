/** @type {import('eslint').Linter.Config} */
module.exports = {
  root: true,
  env: { node: true, es2022: true },
  extends: ['eslint:recommended', 'prettier'],
  parserOptions: { ecmaVersion: 2022, sourceType: 'script' },
  ignorePatterns: ['Workspace/', 'node_modules/'],
  overrides: [
    {
      files: ['tests/unit/**/*.js'],
      parserOptions: { sourceType: 'module' },
    },
  ],
};
