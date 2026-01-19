import Vue from 'vue'
import App from './App.vue'
import VueRouter from 'vue-router'
import axios from 'axios'

import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import HomePage from './components/HomePage.vue'
import UsersPage from './components/UsersPage.vue'
import LogoutPage from './components/LogoutPage.vue'
import SettingsPage from './components/SettingsPage.vue'
import TasksPage from './components/TasksPage.vue'

Vue.config.productionTip = false


axios.defaults.baseURL = '/api'    
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

Vue.use(VueRouter)
Vue.use(Vuetify)

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/home', component: HomePage },
  { path: '/tasks', component: TasksPage },
  { path: '/users', component: UsersPage, meta: { requiresAdmin: true } },
  { path: '/settings', component: SettingsPage },
  { path: '/logout', component: LogoutPage },
]

const router = new VueRouter({
  mode: 'history',
  routes,
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)
  const isLoggedIn = !!localStorage.getItem('username')
  const isAdmin = localStorage.getItem('isAdmin') === 'true'

  if (authRequired && !isLoggedIn) return next('/login')
  if (to.matched.some(r => r.meta.requiresAdmin) && !isAdmin) return next('/home')
  return next()
})

new Vue({
  router,
  vuetify: new Vuetify(),
  render: h => h(App),
}).$mount('#app')
