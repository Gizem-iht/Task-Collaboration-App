<template>
  <v-container fluid>
    <h2 class="mb-4">Users</h2>

    <v-card class="mb-4 pa-3">
      <v-row align="center" no-gutters>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="searchTerm"
            label="Search by email, first name, last name"
            dense
            outlined
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="3" class="mt-2 mt-md-0">
          <v-btn color="primary" class="mr-2" @click="fetchUsers">
            Search
          </v-btn>

          <v-btn v-if="isStaff" color="success" @click="openAddDialog">
            Add
          </v-btn>
        </v-col>
      </v-row>

      <v-alert v-if="error" type="error" dense class="mt-3">
        {{ error }}
      </v-alert>
    </v-card>

    <v-card>
      <v-data-table
        :headers="headers"
        :items="users"
        :loading="loading"
        loading-text="Loading users..."
        class="elevation-1"
        disable-pagination
        hide-default-footer
      >
        <template v-slot:item.actions="{ item }">
          <v-btn
            v-if="isStaff"
            color="red"
            text
            small
            @click="confirmDelete(item)"
          >
            Delete
          </v-btn>
          <span v-else>—</span>
        </template>

        <template v-slot:no-data>
          <div class="pa-4">No users found.</div>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="showAddDialog" max-width="500px">
      <v-card>
        <v-card-title>Add User</v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="newUser.username"
              label="Username"
              dense
              outlined
              class="mb-2"
            ></v-text-field>

            <v-text-field
              v-model="newUser.email"
              label="Email"
              type="email"
              dense
              outlined
              class="mb-2"
            ></v-text-field>

            <v-text-field
              v-model="newUser.first_name"
              label="First name"
              dense
              outlined
              class="mb-2"
            ></v-text-field>

            <v-text-field
              v-model="newUser.last_name"
              label="Last name"
              dense
              outlined
              class="mb-2"
            ></v-text-field>

            <v-text-field
              v-model="newUser.password"
              label="Password"
              type="password"
              dense
              outlined
              class="mb-2"
            ></v-text-field>

            <v-alert v-if="addError" type="error" dense class="mt-2">
              {{ addError }}
            </v-alert>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeAddDialog">Cancel</v-btn>
          <v-btn color="primary" @click="saveUser">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Delete User</v-card-title>
        <v-card-text>
          Are you sure you want to delete
          <strong>{{ userToDelete && userToDelete.username }}</strong>?
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeDeleteDialog">No</v-btn>
          <v-btn color="red" @click="deleteUserConfirmed">Yes</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
  name: "UsersPage",

  data() {
    return {
      users: [],
      loading: false,
      error: null,
      searchTerm: "",

      showAddDialog: false,
      addError: null,
      newUser: {
        username: "",
        email: "",
        first_name: "",
        last_name: "",
        password: "",
      },

      showDeleteDialog: false,
      userToDelete: null,

      isStaff: false,

      headers: [
        { text: "Id", value: "id" },
        { text: "Username", value: "username" },
        { text: "Email", value: "email" },
        { text: "First name", value: "first_name" },
        { text: "Last name", value: "last_name" },
        { text: "Actions", value: "actions", sortable: false },
      ],
    };
  },

  async created() {
    try {
      axios.defaults.withCredentials = true;

      const res = await axios.get("/me/");

      if (!res.data?.encrypted || !res.data?.payload) {
        this.isStaff = false;
        this.$router.replace("/login");
        return;
      }

      const key = process.env.VUE_APP_ENCRYPTION_KEY_B64;
      if (!key) {
        this.isStaff = false;
        this.$router.replace("/login");
        return;
      }

      const me = await decryptMePayload(res.data.payload, key);

      this.isStaff = !!(me?.is_staff || me?.is_superuser);

      if (!this.isStaff) {
        this.$router.replace("/home");
        return;
      }
    } catch (e) {
      this.isStaff = false;
      this.$router.replace("/login");
      return;
    }

    this.fetchUsers();
  },

  methods: {
    async fetchUsers() {
      this.loading = true;
      this.error = null;

      try {
        const res = await axios.get("/users/", {
          params: { q: this.searchTerm || "" },
        });
        this.users = res.data || [];
      } catch (err) {
        this.error = extractErrorMessage(err, "Failed to load users");
      } finally {
        this.loading = false;
      }
    },

    openAddDialog() {
      if (!this.isStaff) return;
      this.showAddDialog = true;
      this.addError = null;
      this.newUser = {
        username: "",
        email: "",
        first_name: "",
        last_name: "",
        password: "",
      };
    },

    closeAddDialog() {
      this.showAddDialog = false;
    },

    async saveUser() {
      if (!this.isStaff) return;

      this.addError = null;
      try {
        await axios.post("/users/", this.newUser);
        this.showAddDialog = false;
        await this.fetchUsers();
      } catch (err) {
        this.addError = extractErrorMessage(err, "Failed to create user");
      }
    },

    confirmDelete(user) {
      if (!this.isStaff) return;
      this.userToDelete = user;
      this.showDeleteDialog = true;
    },

    closeDeleteDialog() {
      this.showDeleteDialog = false;
      this.userToDelete = null;
    },

    async deleteUserConfirmed() {
      if (!this.isStaff || !this.userToDelete) return;

      try {
        await axios.delete(`/users/${this.userToDelete.id}/`);
        this.showDeleteDialog = false;
        this.userToDelete = null;
        await this.fetchUsers();
      } catch (err) {
        alert(extractErrorMessage(err, "Failed to delete user"));
      }
    },
  },
};
</script>

<style scoped>
</style>
