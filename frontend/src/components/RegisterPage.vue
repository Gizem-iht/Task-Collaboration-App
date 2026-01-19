<template>
  <div style="max-width: 400px; margin: 40px auto;">
    <h2>Register</h2>

    <form @submit.prevent="handleRegister">
      <div style="margin-bottom: 10px;">
        <label>Username</label><br />
        <input v-model="username" type="text" required />
      </div>

      <div style="margin-bottom: 10px;">
        <label>Email</label><br />
        <input v-model="email" type="email" required />
      </div>

      <div style="margin-bottom: 10px;">
        <label>Password</label><br />
        <input v-model="password" type="password" required />
      </div>

      <button type="submit">Register</button>
    </form>

    <p v-if="error" style="color: red; margin-top: 10px;">
      {{ error }}
    </p>
    <p v-if="success" style="color: green; margin-top: 10px;">
      ✔ Registration successful! Redirecting to Users page...
    </p>

    <p style="margin-top: 15px;">
      Already have an account?
      <router-link to="/login">Login</router-link>
    </p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RegisterPage",

  data() {
    return {
      username: "",
      email: "",
      password: "",
      error: null,
      success: false,
    };
  },

  methods: {
    async handleRegister() {
      this.error = null;
      this.success = false;

      try {
        const res = await axios.post("/register/", {   
          username: this.username,
          email: this.email,
          password: this.password,
        });

        if (res.data.success) {
          this.success = true;

          setTimeout(() => {
            this.$router.push("/users");
          }, 1200);
        } else {
          this.error = res.data.error || "Registration failed.";
        }
      } catch (err) {
        this.error = err.response?.data?.error || "Registration failed.";
      }
    },
  },
};
</script>
