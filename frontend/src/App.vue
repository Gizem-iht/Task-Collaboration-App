<template>
  <v-app>

    <v-navigation-drawer
      v-if="!isAuthPage"
      app
      v-model="drawer"
      color="#172a3a"
      dark
    >
  
      <v-list dense>
     
        <v-list-item :to="{ path: '/home' }" link>
          <v-list-item-icon>
            <v-icon>mdi-home</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Home</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

   
        <v-list-item :to="{ path: '/tasks' }" link>
          <v-list-item-icon>
            <v-icon>mdi-format-list-checkbox</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Tasks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>


        <v-list-item v-if="isAdmin" :to="{ path: '/users' }" link>
          <v-list-item-icon>
            <v-icon>mdi-account-multiple</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Users</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>


      <template v-slot:append>
        <v-divider></v-divider>

        <v-list-item class="px-3">
          <v-list-item-avatar>
            <v-avatar color="deep-purple accent-4" size="32">
              <span class="white--text text-body-2">
                {{ initials }}
              </span>
            </v-avatar>
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title class="white--text">
              {{ displayName }}
            </v-list-item-title>
          </v-list-item-content>

          <v-menu v-model="userMenu" bottom left>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon v-bind="attrs" v-on="on">
                <v-icon>mdi-chevron-up</v-icon>
              </v-btn>
            </template>

            <v-list>
              <v-list-item @click="goSettings">
                <v-list-item-icon>
                  <v-icon>mdi-cog</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Settings</v-list-item-title>
              </v-list-item>

              <v-list-item @click="handleLogout">
                <v-list-item-icon>
                  <v-icon>mdi-logout</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Logout</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-list-item>
      </template>
    </v-navigation-drawer>


    <v-app-bar
      v-if="!isAuthPage"
      app
      color="white"
      elevate-on-scroll
    >
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title>Task App</v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: "App",

  data() {
    return {
      drawer: true,
      userMenu: false,
    };
  },

  computed: {

    isAuthPage() {
      return this.$route.path === "/login" || this.$route.path === "/register";
    },


    username() {
      return localStorage.getItem("username") || "";
    },

    displayName() {
      return this.username || "Kullanıcı";
    },

    initials() {
      if (!this.username) return "?";
      return this.username
        .split(" ")
        .map((p) => p[0])
        .join("")
        .toUpperCase();
    },


    isAdmin() {
      return localStorage.getItem("isAdmin") === "true";
    },
  },

  methods: {
    handleLogout() {
      localStorage.removeItem("username");
      localStorage.removeItem("email");
      localStorage.removeItem("isAdmin"); 
      this.$router.push("/login");
    },
    goSettings() {
      this.$router.push("/settings");
    },
  },
};
</script>
