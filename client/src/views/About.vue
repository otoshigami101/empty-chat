<template>
  <v-container fill-height>
    <v-row align="center">
      <v-col>
        <h1>
          Empty Chat
          <v-icon>
            mdi-chat
          </v-icon>
        </h1>
        <p>
          Chat App For Who Feels Empty.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  methods: {
    notify(id, username, msg){
      let self = this
      this.$notification.show(username, {
        body: msg
      },
      {
        onclick(){
          self.$router.push({
            name: 'home',
            params: {
              notifHandler: id
            }
          })
        }
      })
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
  created() {
    if(this.isConnectedWS){
      this.$store.dispatch('sendMsgWS',{
        request: 'empty-chat'
      });
    }
  },
  watch: {
    serverWSmsg:{
      immediate: true,
      handler(msg){
        if (msg.data && JSON.parse(msg.data).newMsg) {
          const { newMsg } = JSON.parse(msg.data);
          this.notify(newMsg.id, newMsg.username, newMsg.msg);
        }
      }
    }
  },
}
</script>