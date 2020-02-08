import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import App from './App.vue';
import router from './router';
import store from './store/index';
import vuetify from './plugins/vuetify';
import 'roboto-fontface/css/roboto/roboto-fontface.css';
import '@mdi/font/css/materialdesignicons.css';

axios.defaults.baseURL = 'http://localhost:8081';
Vue.config.productionTip = false;
Vue.use(VueAxios, axios);

Vue.prototype.$app = new Vue({
  router,
  store,
  vuetify,
  render: h => h(App),
  data() {
    return {
      windowHeight: 0,
      windowWidth: 0,
    };
  },

  mounted() {
    this.windowWidth = window.innerWidth;
    this.windowHeight = window.innerHeight;
    this.$nextTick(() => {
      window.addEventListener('resize', this.onResize);
    });
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
  },

  methods: {
    onResize() {
      this.windowWidth = window.innerWidth;
      this.windowHeight = window.innerHeight;
    },
  },
}).$mount('#app');
