/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./memecry/**/*.py", "./memecry/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: ["luxury"],
  },
};
