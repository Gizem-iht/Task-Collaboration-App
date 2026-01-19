<template>
  <div style="max-width: 400px; margin: 40px auto;">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div style="margin-bottom: 10px;">
        <label>Username</label><br />
        <input v-model="username" type="text" />
      </div>
      <div style="margin-bottom: 10px;">
        <label>Password</label><br />
        <input v-model="password" type="password" />
      </div>
      <button type="submit">Login</button>
    </form>

    <p v-if="error" style="color: red; margin-top: 10px;">
      {{ error }}
    </p>

    <p style="margin-top: 15px;">
      Don’t have an account?
      <router-link to="/register">Register</router-link>
    </p>
  </div>
</template>


<script>
import axios from "axios";

export default {
  name: "LoginPage",
  data() {
    return {
      username: "",
      password: "",
      error: null,
    };
  },
  methods: {
    async handleLogin() {
      this.error = null;
      try {
        const res = await axios.post(
          "/login/",   
          {
            username: this.username,
            password: this.password,
          }
        );

        console.log("LOGIN RESPONSE", res.data);

        if (res.data && res.data.success) {
          const uname = res.data.username || this.username;
          const email = res.data.email || "";

          const isAdmin =
            res.data.is_staff === true || res.data.is_superuser === true;

          localStorage.setItem("username", uname);
          localStorage.setItem("email", email);
          localStorage.setItem("isAdmin", isAdmin ? "true" : "false");

          this.$router.push("/home");
        } else {
          this.error = res.data.error || "Login failed";
        }
      } catch (err) {
        console.log("LOGIN ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Login failed";
      }
    },
  },
};
</script>
