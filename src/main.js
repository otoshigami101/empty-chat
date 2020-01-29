import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import 'roboto-fontface/css/roboto/roboto-fontface.css';
import '@mdi/font/css/materialdesignicons.css';

axios.defaults.baseURL = 'api.php';
Vue.config.productionTip = false;
Vue.use(VueAxios, axios);

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App),
}).$mount('#app');
