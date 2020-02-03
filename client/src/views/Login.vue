<template>
    <v-container
        class="fill-height"
      >
        <v-row
          justify="center">
          <v-col
            cols="12"
            sm="8"
            md="4"
          >
            <v-card class="login">
              <v-card-title>Login form</v-card-title>
              <v-card-text>
                <v-form @submit.prevent="login">
                  <v-text-field
                    label="Login"
                    name="login"
                    prepend-icon="mdi-account"
                    type="text"
                    v-model="form.username"
                  />

                  <v-text-field
                    id="password"
                    label="Password"
                    name="password"
                    prepend-icon="mdi-lock"
                    type="password"
                    v-model="form.password"
                  />
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn color="primary" @click="login">Login</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
    </v-container>
</template>
<style scoped>
    .login{
        margin-top: -150px;
    }
</style>
<script>
export default {
  data: () => ({
    sending: false,
    form: {
      username: '',
      password: '',
    },
  }),
  beforeCreate() {
    if (this.$store.state.auth.isLogin) {
      this.$router.push('/');
    }
  },
  methods: {
    login() {
      this.axios.post('/login', this.form).then((r) => {
        if (r.data.jwt_token) {
          localStorage.setItem('jwt_token', r.data.jwt_token);
          this.$router.push('/');
        }
      });
    },
  },
};
</script>
