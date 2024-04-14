/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./memecry/**/*.py"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["luxury", "dim"],
  },
};
