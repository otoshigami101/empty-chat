import Vue from 'vue';
import VueRouter from 'vue-router';
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

  await store.dispatch('check');

  if (AuthRequired && !store.state.auth.isLogin) {
    next('/login');
  }

  next();
});

export default router;
