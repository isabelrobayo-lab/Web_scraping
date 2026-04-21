/** @type {import('vitest').UserConfig} */
module.exports = {
  test: {
    globals: true,
    environment: "node",
    include: ["tests/unit/**/*.test.js"],
    testTimeout: 10000,
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json"],
      reportsDirectory: "./coverage",
    },
  },
};
