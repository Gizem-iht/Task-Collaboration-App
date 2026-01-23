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

    <v-alert v-if="error" type="error" dense class="mb-4">
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
  name: "HomePage",
  data() {
    return {
      username: "",
      isAdminFlag: false,

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
      return this.isAdminFlag === true;
    },
    summaryTitle() {
      return this.isAdmin
        ? "Genel Durum Özeti (tüm kullanıcılar):"
        : "Senin görevlerinin özeti:";
    },
  },

  async created() {
   
    axios.defaults.withCredentials = true;

    
    await this.loadMe();

    await this.loadSummary();
  },

  methods: {
    async loadMe() {
      try {
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

        this.username = me?.username || "";
        this.isAdminFlag = !!(me?.is_staff || me?.is_superuser);
      } catch (err) {
        console.error("Me endpoint failed (HomePage):", err);
       
      }
    },

    async loadSummary() {
      this.loading = true;
      this.error = null;
      this.counts = { todo: 0, inProgress: 0, blocked: 0, done: 0 };

      try {
     
        const url = this.isAdmin ? "/tasks/?all=1" : "/tasks/";

        const res = await axios.get(url);
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
          err.response?.data?.error || "Özet yüklenirken bir hata oluştu.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
