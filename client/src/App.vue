<template>
  <div id="app">
    <v-app>
        <div id="nav" v-if="$store.state.auth.isLogin">
            <router-link to="/">Home</router-link> |
            <router-link to="/about">About</router-link> |
            <router-link to="#" @click.native="$store.dispatch('auth/logout')">logout</router-link>
        </div>
        <v-content>
          <router-view/>
        </v-content>
    </v-app>
  </div>
</template>

<style>
html,body{
  overflow: auto!important;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 15px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
