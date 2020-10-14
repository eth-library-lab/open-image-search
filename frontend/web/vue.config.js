const { useCssModule } = require("vue");

module.exports = {
    devServer: {
        proxy: 'http://localhost:8000/',
    }
  }