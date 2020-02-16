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
    props: true,
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
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 3000,
  });

  next();
});

export default router;
