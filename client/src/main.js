import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import VueNativeSock from 'vue-native-websocket';

import App from './App.vue';
import router from './router';
import store from './store/index';
import vuetify from './plugins/vuetify';
import 'roboto-fontface/css/roboto/roboto-fontface.css';
import '@mdi/font/css/materialdesignicons.css';

axios.defaults.baseURL = 'http://localhost:8081';
Vue.config.productionTip = false;
Vue.use(VueAxios, axios);
if (localStorage.getItem('jwt_token')) {
  Vue.use(VueNativeSock, `ws://localhost:4444?jwt_token=${localStorage.getItem('jwt_token')}`, {
    store,
  });
}

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App),
}).$mount('#app');
