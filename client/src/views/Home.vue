<template>
  <div class="home">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    <v-container fill-height>
      <v-row justify="center">
        <v-col md="8" xs="12">
          <v-card>
            <v-card-title>Chat</v-card-title>
            <v-card-text>
              <div v-if="isConnectedWS">
                <v-list subheader v-if="chats.length">
                  <v-subheader>Recent Chat</v-subheader>
                  <v-list-item v-for="chat in chats" :key="chat.id">
                    <v-list-item-content class="text-left">
                      <v-list-item-title v-text="chat.username"></v-list-item-title>
                    </v-list-item-content>
                    <v-list-item-icon>
                      <v-icon :color="true ? 'green' : 'grey'">mdi-chat</v-icon>
                    </v-list-item-icon>
                  </v-list-item>
                </v-list>
                <div class="text-center" v-else>
                    No chats found.
                </div>
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
    chats() {
      if (this.$store.getters.serverWSmsg.data) {
        if (JSON.parse(this.$store.getters.serverWSmsg.data).chats) {
          return JSON.parse(this.$store.getters.serverWSmsg.data).chats;
        }
      }
      return [];
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
