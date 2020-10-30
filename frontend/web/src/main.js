import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import Vuetify from "vuetify";

createApp(App)
  .use(Vuetify)
  .use(router)
  .mount("#app");
