<template>
  <v-container fluid>

    <div class="d-flex align-center mb-6">
      <h2 class="mr-2">Hoş Geldiniz</h2>
      <span v-if="username" class="font-weight-medium">
        , {{ username }}
      </span>
    </div>

    <div class="mb-4">
      <span class="subtitle-1 font-weight-medium">
        {{ summaryTitle }}
      </span>
    </div>

    <v-alert
      v-if="error"
      type="error"
      dense
      class="mb-4"
    >
      {{ error }}
    </v-alert>

 
    <v-row>
      <v-col cols="12" md="3">
        <v-card class="pa-4" color="#e3f2fd">
          <div class="text-uppercase grey--text text--darken-1 text-subtitle-2">
            TODO
          </div>
          <div class="display-1 font-weight-bold">{{ counts.todo }}</div>
          <div class="mt-2 grey--text text--darken-1">
            Henüz başlanmamış görevler{{ isAdmin ? "" : "in" }}.
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-4" color="#fff3e0">
          <div class="text-uppercase grey--text text--darken-1 text-subtitle-2">
            IN PROGRESS
          </div>
          <div class="display-1 font-weight-bold">{{ counts.inProgress }}</div>
          <div class="mt-2 grey--text text--darken-1">
            Üzerinde çalışılan görevler{{ isAdmin ? "" : "in" }}.
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-4" color="#ffebee">
          <div class="text-uppercase grey--text text--darken-1 text-subtitle-2">
            BLOCKED
          </div>
          <div class="display-1 font-weight-bold">{{ counts.blocked }}</div>
          <div class="mt-2 grey--text text--darken-1">
            Takılan / engellenen görevler{{ isAdmin ? "" : "in" }}.
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-4" color="#e8f5e9">
          <div class="text-uppercase grey--text text--darken-1 text-subtitle-2">
            DONE
          </div>
          <div class="display-1 font-weight-bold">{{ counts.done }}</div>
          <div class="mt-2 grey--text text--darken-1">
            Tamamlanan görevler{{ isAdmin ? "" : "in" }}.
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import axios from "axios";

export default {
  name: "HomePage",
  data() {
    return {
      username: "",
      counts: {
        todo: 0,
        inProgress: 0,
        blocked: 0,
        done: 0,
      },
      error: null,
      loading: false,
    };
  },
  computed: {
    isAdmin() {
      return localStorage.getItem("isAdmin") === "true";
    },
    summaryTitle() {
      return this.isAdmin
        ? "Genel Durum Özeti (tüm kullanıcılar):"
        : "Senin görevlerinin özeti:";
    },
  },
  created() {
    this.initUser();
    this.loadSummary();
  },
  methods: {
    initUser() {
      const stored = localStorage.getItem("username");
      if (stored) {
        this.username = stored;
        return;
      }

      axios
        .get("/me/") 
        .then((res) => {
          this.username = res.data.username || "";
          if (this.username) {
            localStorage.setItem("username", this.username);
          }
        })
        .catch((err) => {
          console.error("Me endpoint failed (HomePage):", err);
        });
    },

    async loadSummary() {
      this.loading = true;
      this.error = null;
      this.counts = { todo: 0, inProgress: 0, blocked: 0, done: 0 };

      try {
        const res = await axios.get("/tasks/"); 
        const tasks = res.data || [];

        tasks.forEach((t) => {
          switch ((t.state || "").toUpperCase()) {
            case "TODO":
              this.counts.todo += 1;
              break;
            case "IN_PROGRESS":
              this.counts.inProgress += 1;
              break;
            case "BLOCKED":
              this.counts.blocked += 1;
              break;
            case "DONE":
              this.counts.done += 1;
              break;
          }
        });
      } catch (err) {
        console.error("LOAD SUMMARY ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Özet yüklenirken bir hata oluştu.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
