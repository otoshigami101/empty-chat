import axios from 'axios';

const auth = {
  state: {
    isLogin: true,
    user: [],
  },
  actions: {
    check({ state }) {
      return axios.post('/validate_login', { token: localStorage.getItem('token') })
        .then((r) => {
          state.user = r.data.data;
          state.isLogin = true;
        }).catch((e) => {
          console.log(e);
          state.isLogin = false;
        });
    },
    logout() {
      localStorage.removeItem('token');
      window.location.reload();
    },
  },
};

export default auth;
