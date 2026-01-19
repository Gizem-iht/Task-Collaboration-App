<template>
  <v-container>
    <h2 class="mb-4">Tasks</h2>

    <v-alert v-if="error" type="error" dense class="mb-4">
      {{ error }}
    </v-alert>

    <v-card>
      <v-card-title class="d-flex align-center">
        <v-text-field
          v-model="search"
          label="Search by title / description / owner / state"
          dense
          clearable
          hide-details
          class="mr-4"
        ></v-text-field>

        <v-spacer></v-spacer>

        <v-btn color="primary" dark @click="openAddDialog">
          ADD TASK
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-simple-table>
          <thead>
            <tr>
              <th class="text-left">Id</th>
              <th class="text-left">Title</th>
              <th class="text-left">Description</th>
              <th class="text-left">Owner</th>
              <th class="text-left">State</th>
              <th class="text-center" style="width: 110px;">Delete</th>
              <th class="text-center" style="width: 130px;">Comments</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in filteredTasks" :key="task.id">
              <td>{{ task.id }}</td>

              <td>
                <div
                  v-if="editTitleId !== task.id"
                  @click="startEditTitle(task)"
                  class="title-cell"
                >
                  {{ task.title || "—" }}
                </div>

                <v-text-field
                  v-else
                  v-model="editTitleValue"
                  dense
                  solo
                  hide-details
                  autofocus
                  @blur="saveTitle(task)"
                  @keyup.enter="saveTitle(task)"
                  @keyup.esc="cancelTitleEdit"
                ></v-text-field>
              </td>

              <td>
                <div class="description-cell">
                  {{ task.description || "—" }}
                </div>
              </td>

              <td>{{ task.owner_username || "—" }}</td>

              <td>
                <v-menu
                  v-model="stateMenu[task.id]"
                  :close-on-content-click="false"
                  offset-y
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-chip
                      v-bind="attrs"
                      v-on="on"
                      :color="stateColor(task.state)"
                      dark
                      label
                      class="text-uppercase"
                      style="cursor: pointer;"
                    >
                      {{ task.state }}
                    </v-chip>
                  </template>

                  <v-list dense>
                    <v-list-item
                      v-for="s in stateOptions"
                      :key="s"
                      @click="changeState(task, s)"
                    >
                      <v-list-item-title class="text-uppercase">
                        {{ s }}
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </td>

              <td class="text-center">
                <v-btn
                  small
                  text
                  color="red darken-1"
                  @click="deleteTask(task)"
                >
                  <v-icon left small>mdi-delete</v-icon>
                  Delete
                </v-btn>
              </td>

              <td class="text-center">
                <v-btn
                  small
                  text
                  color="primary"
                  @click="openComments(task)"
                >
                  <v-icon left small>mdi-comment-text-outline</v-icon>
                  Comments
                </v-btn>
              </td>
            </tr>

            <tr v-if="!loading && filteredTasks.length === 0">
              <td colspan="7" class="text-center grey--text">
                No tasks found.
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card-text>
    </v-card>

    <v-expand-transition>
      <div v-if="selectedTask" class="mt-4">
        <v-card>
          <v-card-title>
            Comments – #{{ selectedTask.id }} {{ selectedTask.title }}
            <v-spacer></v-spacer>
            <v-btn icon small @click="closeComments">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-text class="comments-area">
            <div v-if="commentsLoading" class="grey--text text-center mb-2">
              Loading comments...
            </div>

            <div
              v-else-if="comments.length === 0"
              class="grey--text text-center mb-2"
            >
              No comments yet. Be the first to write ✍️
            </div>

            <div v-else>
              <div
                v-for="c in comments"
                :key="c.id"
                class="comment-row"
                :class="{ 'comment-mine': c.author_username === currentUsername }"
              >
                <div class="comment-meta">
                  <strong>{{ c.author_username }}</strong>
                  <span class="comment-date">{{ formatDate(c.created_at) }}</span>
                </div>
                <div class="comment-bubble">
                  {{ c.content }}
                </div>
              </div>
            </div>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions>
            <v-text-field
              v-model="newComment"
              label="Write a message..."
              outlined
              dense
              hide-details
              @keyup.enter="sendComment"
            ></v-text-field>
            <v-btn
              color="primary"
              :disabled="!newComment.trim() || !selectedTask"
              @click="sendComment"
            >
              Send
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
    </v-expand-transition>

    <v-dialog v-model="addDialog" max-width="600px">
      <v-card>
        <v-card-title>Add New Task</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newTaskTitle"
            label="Title"
            required
            class="mb-3"
          ></v-text-field>

          <v-textarea
            v-model="newTaskDescription"
            label="Description"
            rows="3"
            class="mb-3"
          ></v-textarea>

          <v-select
            v-model="newTaskState"
            :items="stateOptions"
            label="State"
            class="mb-3"
          ></v-select>

          <v-select
            v-if="isAdmin"
            v-model="newTaskOwnerId"
            :items="usersForSelect"
            item-text="label"
            item-value="value"
            label="Owner"
            class="mb-3"
            clearable
            hint="Boş bırakırsan owner = sen"
            persistent-hint
          ></v-select>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeAddDialog">Cancel</v-btn>
          <v-btn color="primary" dark @click="createTask">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  name: "TasksPage",
  data() {
    return {
      tasks: [],
      loading: false,
      error: null,

      search: "",

      editTitleId: null,
      editTitleValue: "",

      stateMenu: {},

      stateOptions: ["TODO", "IN_PROGRESS", "BLOCKED", "DONE"],

      addDialog: false,
      newTaskTitle: "",
      newTaskDescription: "",
      newTaskState: "TODO",
      newTaskOwnerId: null,

      users: [],

      selectedTask: null,
      comments: [],
      commentsLoading: false,
      newComment: "",
    };
  },
  computed: {
    isAdmin() {
      return localStorage.getItem("isAdmin") === "true";
    },

    currentUsername() {
      return localStorage.getItem("username") || "";
    },

    filteredTasks() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.tasks;

      return this.tasks.filter((t) => {
        const title = (t.title || "").toLowerCase();
        const desc = (t.description || "").toLowerCase();
        const owner = (t.owner_username || "").toLowerCase();
        const state = (t.state || "").toLowerCase();
        return (
          title.includes(q) ||
          desc.includes(q) ||
          owner.includes(q) ||
          state.includes(q)
        );
      });
    },

    usersForSelect() {
      return this.users.map((u) => ({
        value: u.id,
        label: u.username + (u.email ? ` (${u.email})` : ""),
      }));
    },
  },
  created() {
    this.loadTasks();
    if (this.isAdmin) {
      this.loadUsers();
    }
  },
  methods: {
    async loadTasks() {
      this.loading = true;
      this.error = null;
      try {
     
        const res = await axios.get("/tasks/?all=1");
        this.tasks = res.data || [];
      } catch (err) {
        console.error("LOAD TASKS ERROR", err);
        this.error = "Tasks could not be loaded.";
      } finally {
        this.loading = false;
      }
    },

    async loadUsers() {
      try {
        const res = await axios.get("/users/");
        this.users = res.data || [];
      } catch (err) {
        console.error("LOAD USERS ERROR", err);
      }
    },

    startEditTitle(task) {
      this.editTitleId = task.id;
      this.editTitleValue = task.title;
    },
    cancelTitleEdit() {
      this.editTitleId = null;
      this.editTitleValue = "";
    },
    async saveTitle(task) {
      const newTitle = (this.editTitleValue || "").trim();
      if (!newTitle || newTitle === task.title) {
        this.cancelTitleEdit();
        return;
      }

      const originalTitle = task.title;
      task.title = newTitle;
      this.cancelTitleEdit();

      try {
        await this.updateTaskOnServer(task);
      } catch (err) {
        task.title = originalTitle;
      }
    },

    stateColor(state) {
      switch (state) {
        case "TODO":
          return "blue lighten-4";
        case "IN_PROGRESS":
          return "amber lighten-3";
        case "BLOCKED":
          return "red lighten-4";
        case "DONE":
          return "green lighten-4";
        default:
          return "grey lighten-2";
      }
    },
    async changeState(task, newState) {
      if (task.state === newState) {
        this.stateMenu = { ...this.stateMenu, [task.id]: false };
        return;
      }

      const originalState = task.state;
      task.state = newState;
      this.stateMenu = { ...this.stateMenu, [task.id]: false };

      try {
        await this.updateTaskOnServer(task);
      } catch (err) {
        task.state = originalState;
      }
    },

    async updateTaskOnServer(task) {
      try {
        const payload = {
          title: task.title,
          description: task.description || "",
          state: task.state,
        };

        const res = await axios.put(`/tasks/${task.id}/`, payload);

        if (res.data && res.data.task) {
          Object.assign(task, res.data.task);
        }
      } catch (err) {
        console.error("UPDATE TASK ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Task could not be updated.";
        throw err;
      }
    },

    async deleteTask(task) {
      if (!confirm(`Delete task #${task.id}?`)) return;

      try {
        await axios.delete(`/tasks/${task.id}/`);
        this.tasks = this.tasks.filter((t) => t.id !== task.id);

        if (this.selectedTask && this.selectedTask.id === task.id) {
          this.closeComments();
        }
      } catch (err) {
        console.error("DELETE TASK ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Task could not be deleted.";
      }
    },

    openComments(task) {
      this.selectedTask = task;
      this.comments = [];
      this.newComment = "";
      this.loadComments();
    },

    closeComments() {
      this.selectedTask = null;
      this.comments = [];
      this.newComment = "";
    },

    async loadComments() {
      if (!this.selectedTask) return;
      this.commentsLoading = true;
      try {
        const res = await axios.get(`/tasks/${this.selectedTask.id}/comments/`);
        this.comments = res.data || [];
      } catch (err) {
        console.error("LOAD COMMENTS ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Comments could not be loaded.";
      } finally {
        this.commentsLoading = false;
      }
    },

    async sendComment() {
      const text = (this.newComment || "").trim();
      if (!text || !this.selectedTask) return;

      try {
        const res = await axios.post(`/tasks/${this.selectedTask.id}/comments/`, {
          content: text,
        });

        if (res.data && res.data.comment) {
          this.comments.push(res.data.comment);
        }
        this.newComment = "";
      } catch (err) {
        console.error("SEND COMMENT ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Comment could not be sent.";
      }
    },

    formatDate(iso) {
      if (!iso) return "";
      const d = new Date(iso);
      return d.toLocaleString();
    },

    openAddDialog() {
      this.addDialog = true;
      this.newTaskTitle = "";
      this.newTaskDescription = "";
      this.newTaskState = "TODO";
      this.newTaskOwnerId = null;
    },
    closeAddDialog() {
      this.addDialog = false;
    },
    async createTask() {
      const title = (this.newTaskTitle || "").trim();
      if (!title) {
        this.error = "Title is required.";
        return;
      }

      const payload = {
        title,
        description: this.newTaskDescription || "",
        state: this.newTaskState || "TODO",
      };

      if (this.isAdmin && this.newTaskOwnerId) {
        payload.owner_id = this.newTaskOwnerId;
      }

      try {
        const res = await axios.post("/tasks/", payload);

        if (res.data && res.data.task) {
          this.tasks.push(res.data.task);
        }

        this.closeAddDialog();
        this.error = null;
      } catch (err) {
        console.error("CREATE TASK ERROR", err);
        this.error =
          (err.response && err.response.data && err.response.data.error) ||
          "Task could not be created.";
      }
    },
  },
};
</script>

<style>
.title-cell {
  cursor: text;
  white-space: normal !important;
  word-break: break-word !important;
  max-width: 250px;
  line-height: 1.4;
}

.description-cell {
  white-space: normal;
  word-break: break-word;
  max-width: 350px;
  line-height: 1.4;
}

.comments-area {
  max-height: 300px;
  overflow-y: auto;
}

.comment-row {
  margin-bottom: 10px;
  max-width: 70%;
}

.comment-mine {
  margin-left: auto;
  text-align: right;
}

.comment-meta {
  font-size: 11px;
  color: #777;
  margin-bottom: 3px;
}

.comment-bubble {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 16px;
  background: #f1f1f1;
}

.comment-mine .comment-bubble {
  background: #1976d2;
  color: white;
}

.comment-date {
  margin-left: 6px;
}
</style>
