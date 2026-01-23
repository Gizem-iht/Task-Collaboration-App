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

function extractErrorMessage(err) {
 

  const data = err?.response?.data;

  if (!data) return "Registration failed.";

  if (typeof data === "string") return data;

  if (data.error) return data.error;
  if (data.detail) return data.detail;


  if (data.password && Array.isArray(data.password) && data.password.length > 0) {
    return data.password[0];
  }
  if (data.username && Array.isArray(data.username) && data.username.length > 0) {
    return data.username[0];
  }
  if (data.email && Array.isArray(data.email) && data.email.length > 0) {
    return data.email[0];
  }
  if (data.non_field_errors && Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    return data.non_field_errors[0];
  }

  const keys = Object.keys(data);
  if (keys.length > 0) {
    const firstVal = data[keys[0]];
    if (Array.isArray(firstVal) && firstVal.length > 0) return firstVal[0];
    if (typeof firstVal === "string") return firstVal;
  }

  return "Registration failed.";
}

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
        
        axios.defaults.withCredentials = true;

        const res = await axios.post("/register/", {
          username: this.username,
          email: this.email,
          password: this.password,
        });

        if (res.data?.success) {
          this.success = true;

          setTimeout(() => {
            this.$router.push("/users");
          }, 1200);
        } else {
          this.error = res.data?.error || "Registration failed.";
        }
      } catch (err) {
        console.log("REGISTER ERROR", err);
        this.error = extractErrorMessage(err);
      }
    },
  },
};
</script>
