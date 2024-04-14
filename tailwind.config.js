/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./memecry/**/*.py"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: ["luxury"],
  },
};
