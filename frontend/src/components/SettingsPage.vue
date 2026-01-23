<template>
  <v-container class="mt-4" style="max-width: 800px;">
    <h2 class="mb-4">Settings</h2>

    <v-card class="mb-4">
      <v-card-title>Profile Information</v-card-title>
      <v-card-text>
        <v-form>
          <v-text-field
            v-model="profile.first_name"
            label="First name"
            dense
            outlined
            class="mb-2"
          ></v-text-field>

          <v-text-field
            v-model="profile.last_name"
            label="Last name"
            dense
            outlined
            class="mb-2"
          ></v-text-field>

          <v-text-field
            v-model="profile.email"
            label="Email"
            type="email"
            dense
            outlined
            class="mb-2"
          ></v-text-field>

          <v-alert v-if="profileError" type="error" dense class="mt-2">
            {{ profileError }}
          </v-alert>

          <v-alert v-if="profileSuccess" type="success" dense class="mt-2">
            {{ profileSuccess }}
          </v-alert>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="saveProfile">Save Profile</v-btn>
      </v-card-actions>
    </v-card>

    <v-card class="mb-4">
      <v-card-title>Change Password</v-card-title>
      <v-card-text>
        <v-form>
          <v-text-field
            v-model="password.old_password"
            label="Current password"
            type="password"
            dense
            outlined
            class="mb-2"
          ></v-text-field>

          <v-text-field
            v-model="password.new_password1"
            label="New password"
            type="password"
            dense
            outlined
            class="mb-2"
          ></v-text-field>

          <v-text-field
            v-model="password.new_password2"
            label="Repeat new password"
            type="password"
            dense
            outlined
            class="mb-2"
          ></v-text-field>

          <v-alert v-if="passwordError" type="error" dense class="mt-2">
            {{ passwordError }}
          </v-alert>

          <v-alert v-if="passwordSuccess" type="success" dense class="mt-2">
            {{ passwordSuccess }}
          </v-alert>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="changePassword">Change Password</v-btn>
      </v-card-actions>
    </v-card>

    <v-card class="mb-4" outlined>
      <v-card-title class="red--text">Delete Account</v-card-title>
      <v-card-text>
        <p class="mb-2">
          Bu işlem geri alınamaz. Hesabınızı ve tüm kullanıcı verinizi kalıcı
          olarak silmek istediğinizden emin olun.
        </p>

        <v-text-field
          v-model="deletePassword"
          label="Confirm with your password"
          type="password"
          dense
          outlined
          class="mb-2"
        ></v-text-field>

        <v-alert v-if="deleteError" type="error" dense class="mt-2">
          {{ deleteError }}
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red" text @click="deleteAccount">Delete My Account</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
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

function extractErrorMessage(err, fallback) {
  const data = err?.response?.data;
  if (!data) return fallback;

  if (typeof data === "string") return data;
  if (data.error) return data.error;
  if (data.detail) return data.detail;

  const keys = Object.keys(data);
  if (keys.length > 0) {
    const v = data[keys[0]];
    if (Array.isArray(v) && v.length > 0) return v[0];
    if (typeof v === "string") return v;
  }

  return fallback;
}

export default {
  name: "SettingsPage",

  data() {
    return {
      profile: {
        first_name: "",
        last_name: "",
        email: "",
      },
      profileError: null,
      profileSuccess: null,

      password: {
        old_password: "",
        new_password1: "",
        new_password2: "",
      },
      passwordError: null,
      passwordSuccess: null,

      deletePassword: "",
      deleteError: null,
    };
  },

  async created() {
    try {
      axios.defaults.withCredentials = true;

      const res = await axios.get("/me/");

     
      if (!res.data?.encrypted || !res.data?.payload) {
        console.error("Expected encrypted /me response, got:", res.data);
        return;
      }

      const key = process.env.VUE_APP_ENCRYPTION_KEY_B64;
      if (!key) {
        console.error("Missing VUE_APP_ENCRYPTION_KEY_B64 in .env");
        return;
      }

      const me = await decryptMePayload(res.data.payload, key);

      if (me && me.isAuthenticated) {
        this.profile.first_name = me.first_name || "";
        this.profile.last_name = me.last_name || "";
        this.profile.email = me.email || "";
      }
    } catch (err) {
      console.error("Failed to load profile info:", err);
    }
  },

  methods: {
    async saveProfile() {
      this.profileError = null;
      this.profileSuccess = null;

      try {
        axios.defaults.withCredentials = true;

        const res = await axios.post("/profile/update/", {
          first_name: this.profile.first_name,
          last_name: this.profile.last_name,
          email: this.profile.email,
        });

        if (res.data?.success) {
          this.profileSuccess = "Profile has been updated successfully.";
        } else {
          this.profileError = res.data?.error || "Failed to update profile.";
        }
      } catch (err) {
        console.log("update_profile error:", err.response?.status, err.response?.data);
        this.profileError = extractErrorMessage(err, "Failed to update profile.");
      }
    },

    async changePassword() {
      this.passwordError = null;
      this.passwordSuccess = null;

      try {
        axios.defaults.withCredentials = true;

        const res = await axios.post("/password/change/", {
          old_password: this.password.old_password,
          new_password1: this.password.new_password1,
          new_password2: this.password.new_password2,
        });

        if (res.data?.success) {
          this.passwordSuccess = "Password has been changed successfully.";
          this.password.old_password = "";
          this.password.new_password1 = "";
          this.password.new_password2 = "";
        } else {
          this.passwordError = res.data?.error || "Failed to change password.";
        }
      } catch (err) {
        this.passwordError = extractErrorMessage(err, "Failed to change password.");
      }
    },

    async deleteAccount() {
      this.deleteError = null;

      if (!this.deletePassword) {
        this.deleteError = "Please enter your password.";
        return;
      }

      if (!confirm("Are you sure you want to delete your account?")) {
        return;
      }

      try {
        axios.defaults.withCredentials = true;

        const res = await axios.post("/account/delete/", {
          password: this.deletePassword,
        });

        if (res.data?.success) {
        
          this.$router.push("/login");
        } else {
          this.deleteError = res.data?.error || "Failed to delete account.";
        }
      } catch (err) {
        this.deleteError = extractErrorMessage(err, "Failed to delete account.");
      }
    },
  },
};
</script>

<style scoped>
.mb-2 {
  margin-bottom: 8px;
}
.mb-4 {
  margin-bottom: 16px;
}
.mt-4 {
  margin-top: 16px;
}
</style>
