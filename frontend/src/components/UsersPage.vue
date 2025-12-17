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

     
          <v-btn
            v-if="isStaff"
            color="success"
            @click="openAddDialog"
          >
            Add
          </v-btn>
        </v-col>
      </v-row>

      <v-alert
        v-if="error"
        type="error"
        dense
        class="mt-3"
      >
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

            <v-alert
              v-if="addError"
              type="error"
              dense
              class="mt-2"
            >
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
        <v-card-title class="headline">
          Delete User
        </v-card-title>
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
      const res = await axios.get("/api/me/", { withCredentials: true });

    
      this.isStaff = !!res.data.is_staff;

  
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
        const res = await axios.get("/api/users/", {
          params: { q: this.searchTerm || "" },
          withCredentials: true,
        });
        this.users = res.data;
      } catch (err) {
        this.error = err.response?.data?.error || "Failed to load users";
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
        await axios.post("/api/users/", this.newUser, {
          withCredentials: true,
        });
        this.showAddDialog = false;
        await this.fetchUsers();
      } catch (err) {
        this.addError =
          err.response?.data?.error || "Failed to create user";
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
        await axios.delete(`/api/users/${this.userToDelete.id}/`, {
          withCredentials: true,
        });
        this.showDeleteDialog = false;
        this.userToDelete = null;
        await this.fetchUsers();
      } catch (err) {
        alert(
          err.response?.data?.error || "Failed to delete user"
        );
      }
    },
  },
};
</script>

<style scoped>
</style>
