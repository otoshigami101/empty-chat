<template>
  <div class="home">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    <v-container fill-height>
      <v-row justify="center">
        <v-col cols="12">
          <v-card>
            <v-card-title>
                List Users
                <v-spacer></v-spacer>
                <v-btn
                    icon
                    @click="show_user = !show_user"
                >
                    <v-icon>{{ show_user ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                </v-btn>
            </v-card-title>
            <v-expand-transition>
              <div v-show="show_user">
                <v-card-text>
                  <v-list v-if="users.length > 0">
                      <v-list-item @click="startChat(user.id)"
                        v-for="user in users" :key="user.id">
                        <v-list-item-content class="text-left">
                          <v-list-item-title v-text="user.username"></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                  </v-list>
                  <div class="text-center" v-else>
                      No chats found.
                  </div>
                </v-card-text>
              </div>
            </v-expand-transition>
          </v-card>
        </v-col>
        <v-col md="4" cols="12">
          <v-card>
            <v-card-title>Chats</v-card-title>
            <v-card-text>
              <div v-if="isConnectedWS">
                <v-list v-if="chats.length">
                  <v-list-item v-for="chat in chats" :key="chat.id"
                  @click="startChat(chat.id)">
                    <v-list-item-content class="text-left">
                      <v-list-item-title v-text="chat.username"></v-list-item-title>
                    </v-list-item-content>
                    <v-list-item-icon>
                      <v-icon :color="true ? 'green' : 'grey'">mdi-chat</v-icon>
                    </v-list-item-icon>
                  </v-list-item>
                </v-list>
                <div class="text-center" v-else>
                    <b>No chats found.</b>
                    <p>Select User to start the conversation</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col md="8" cols="12">
            <v-card>
              <v-card-title>
                {{ current_chat.username ? current_chat.username : 'WELCOME TO EMPTY CHAT' }}
              </v-card-title>
              <v-divider></v-divider>
              <v-card-text 
                class="pa-5" 
                id="conversations-container"
                style="height: 300px; overflow: auto; background-color: #ddd; padding: 15px;">
                <v-row v-for="(conversation, index) in conversations" :key="index">
                    <v-col cols="12" class="ma-n2" v-if="conversation.sender == current_chat.id">
                        <div class="chat-buble left">
                          <span class="text">
                            {{ conversation.msg }}
                          </span>
                        </div>
                    </v-col>
                    <v-col cols="12" class="ma-n2" v-else>
                      <div class="chat-buble right">
                        <span class="text" >
                          {{ conversation.msg }}
                        </span>
                      </div>
                    </v-col>
                </v-row>
                <div v-if="conversations.length == 0">
                  <v-icon x-large>
                      mdi-chat
                    </v-icon>
                    <h3>
                      Please choose a message to start the conversation
                    </h3>
                </div>
              </v-card-text>
            <v-divider></v-divider>
            <v-card-actions v-if="conversations.length > 0">
                <v-text-field
                placeholder="Type a message..."
                outlined
                rounded
                dense
                v-model="message"
                @keypress.enter="sendChat"
                />
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<style scoped>
  .chat-buble{
    background-color: #fff;
    padding: 10px;
    max-width: 50%;
    text-align: left;
  }
  .chat-buble.left{
    float: left;
    border-radius: 0px 10px 10px 15px;
  }
  .chat-buble.right{
    float: right;
    border-radius: 10px 0px 15px 10px;
  }
  .chat-buble .text{
    line-height: 1.5em;
    position: relative;z-index: 1;
  }
</style>
<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue';
import $ from 'jquery';

export default {
  name: 'home',
  data: () => ({
    show_user: false,
    users: [],
    current_chat: [],
    message: '',
    chats: [],
    conversations: [],
    sendingChat:false,
  }),
  created() {
    this.getUsers();
  },
  methods: {
    getChats() {
      this.$store.dispatch('sendMsgWS', { request: 'chats' });
    },
    getUsers() {
      this.axios.get('/users', {
        params:
        { except: this.$store.state.auth.user.id },
      }).then((r) => {
        this.users = r.data.users;
      }).catch((e) => {
        alert(JSON.stringify(e));
      });
    },
    startChat(id) {
      if (this.current_chat.id !== id) {
        this.axios.post('/user', { id }).then((r) => {
          this.current_chat = r.data;
          this.getConversation();
        }).catch(() => {
          this.current_chat = [];
          alert('failed to start conversation');
        });
      }
    },
    getConversation() {
      this.$store.dispatch('sendMsgWS', { request: 'conversations', userId: this.current_chat.id });
    },
    async sendChat() {
      if (this.message !== '') {
        let maxLength = 4000
        let partMsg = Math.ceil(this.message.length / maxLength)
        if(partMsg > 1){
          alert('the message is too long, the message will send in multiple parts. ')
        }
        for (let i = 0; i <= partMsg; i++){
            let message = this.message.substr(i*maxLength, maxLength*(i+1))
            this.$store.dispatch('sendMsgWS', {
              request: 'send_chat',
              userId: this.current_chat.id,
              message: message,
            });
            await this.dynamicWatch(this,() => this.serverWSmsg);
        }

        this.message = '';
      }
    },
    dynamicWatch(vm, fn){
      return new Promise(resolve => {
        const watcher = vm.$watch(fn, (newVal) => {
          resolve(newVal);
          watcher(); // cleanup;
        });
      });
    },
    focusNewChat(){
      let el = $('#conversations-container')
      if(el.length) {
        var h = el.get(0).scrollHeight;
        el.scrollTop(h);
      }
    }
  },
  computed: {
    isConnectedWS() {
      return this.$store.getters.isConnectedWS;
    },
    serverWSmsg() {
      return this.$store.getters.serverWSmsg;
    },
    sending_chat(){
      return this.sendingChat
    }
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
    serverWSmsg: {
      immediate: true,
      deep: true,
      handler(msg) {
        if (msg.data) {
          if (JSON.parse(msg.data).conversations) {
            this.conversations = JSON.parse(msg.data).conversations;
            this.sendingChat = false
            this.$nextTick(() => {
              this.focusNewChat()
            })
          } else if (JSON.parse(msg.data).chats) {
            this.chats = JSON.parse(msg.data).chats;
          }
        }
      },
    },
  },
};
</script>
