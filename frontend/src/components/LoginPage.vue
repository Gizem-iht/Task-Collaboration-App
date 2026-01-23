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

function b64ToBytes(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

async function importAesKeyFromBase64(base64Key32bytes) {
  const raw = b64ToBytes(base64Key32bytes);
  return crypto.subtle.importKey("raw", raw, "AES-GCM", false, ["decrypt"]);
}

async function decryptMePayload(payload, base64Key) {
  const key = await importAesKeyFromBase64(base64Key);
  const iv = b64ToBytes(payload.iv);
  const data = b64ToBytes(payload.data);

  const plainBuf = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    key,
    data
  );

  const plainText = new TextDecoder().decode(new Uint8Array(plainBuf));
  return JSON.parse(plainText);
}

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
 
        axios.defaults.withCredentials = true;

        const res = await axios.post("/login/", {
          username: this.username,
          password: this.password,
        });

        console.log("LOGIN RESPONSE", res.data);

        if (!res.data || res.data.success !== true) {
          this.error = res.data?.error || "Login failed";
          return;
        }

   
        const meRes = await axios.get("/me/");
        console.log("ME ENCRYPTED RESPONSE", meRes.data);

        if (!meRes.data?.encrypted || !meRes.data?.payload) {
          this.error = "Expected encrypted /me response but got something else.";
          return;
        }

        const key = process.env.VUE_APP_ENCRYPTION_KEY_B64;
        if (!key) {
          this.error = "Missing VUE_APP_ENCRYPTION_KEY_B64 in frontend .env";
          return;
        }

        const mePlain = await decryptMePayload(meRes.data.payload, key);
        console.log("ME DECRYPTED", mePlain);

        this.$router.push("/home");
      } catch (err) {
        console.log("LOGIN ERROR", err);
        this.error =
          err.response?.data?.error ||
          err.response?.data?.detail ||
          "Login failed";
      }
    },
  },
};
</script>
