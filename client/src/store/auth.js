import axios from 'axios';

const auth = {
  namespaced: true,
  state: {
    isLogin: true,
    user: [],
  },
  actions: {
    check({ state }) {
      return axios.post('/validate_login', { jwt_token: localStorage.getItem('jwt_token') })
        .then((r) => {
          if (r.data.data) {
            state.user = r.data.data;
            state.isLogin = true;
          } else {
            state.isLogin = false;
          }
        }).catch((e) => {
          console.log(e);
          state.isLogin = false;
        });
    },
    logout() {
      localStorage.removeItem('jwt_token');
      window.location.reload();
    },
  },
};

export default auth;
