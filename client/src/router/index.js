import Vue from 'vue';
import VueRouter from 'vue-router';
import VueNativeSock from 'vue-native-websocket';
import Home from '../views/Home.vue';
import store from '../store/index';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "about" */ '../views/Login.vue'),
  },
];


const router = new VueRouter({
  mode: 'history',
  routes,
});

router.beforeEach(async (request, from, next) => {
  const guestPage = ['/login'];
  const AuthRequired = !guestPage.includes(request.path);

  await store.dispatch('auth/check');

  if (AuthRequired && !store.state.auth.isLogin) {
    next('/login');
  }

  Vue.use(VueNativeSock, `ws://localhost:4444?uid=${store.state.auth.user.id}`, {
    store,
    reconnection: true, // (Boolean) whether to reconnect automatically (false)
    reconnectionAttempts: Infinity, // (Number) number of reconnection attempts before giving up (Infinity),
    reconnectionDelay: 3000, // (Number) how long to initially wait before attempting a new (1000)
  });

  next();
});

export default router;
