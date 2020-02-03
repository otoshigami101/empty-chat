<template>
  <div class="home">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    <v-container fill-height>
      <v-row justify="center">
        <v-col md="8" xs="12">
          <v-card>
            <v-card-title>
              Chat
            </v-card-title>
            <v-card-text>
               <v-list subheader>
                <v-subheader>User</v-subheader>
                <v-list-item @click="getChats">
                  <v-list-item-avatar>
                    <v-img src="https://cdn.vuetifyjs.com/images/lists/3.jpg"></v-img>
                  </v-list-item-avatar>

                  <v-list-item-content class="text-left">
                    <v-list-item-title v-text="'username'"></v-list-item-title>
                  </v-list-item-content>
                  <v-list-item-icon>
                    <v-icon :color="true ? 'green' : 'grey'">mdi-chat</v-icon>
                  </v-list-item-icon>
                </v-list-item>
              </v-list>
              <div v-if="isConnectedWS">
                <label for="">
                  Server Message :
                </label>
                <div>{{ serverWSmsg.data }}</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue';

export default {
  name: 'home',
  methods: {
    getChats() {
      this.$store.dispatch('sendMsgWS', { request: 'chats' });
    },
  },
  computed: {
    isConnectedWS() {
      return this.$store.getters.isConnectedWS;
    },
    serverWSmsg() {
      return this.$store.getters.serverWSmsg;
    },
  },
  watch: {
    isConnectedWS: {
      immediate: true,
      handler(connected) {
        if (connected) {
          this.getChats();
        }
      },
    },
  },
};
</script>
