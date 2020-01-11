import Vue from 'vue'
import App from './App.vue'
import Register from './components/Register.vue'
import Login from './components/Login.vue'
import Index from './components/Index.vue'
import Items from './components/Items.vue'

// font-awesome stuff
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faPlus } from '@fortawesome/free-solid-svg-icons'
library.add(faPlus)
Vue.component('font-awesome-icon', FontAwesomeIcon)

import store from './store'

Vue.config.productionTip = false

// axios
import axios from 'axios'
import VueAxios from 'vue-axios'

Vue.use(VueAxios, axios)
// end axios

// vue router
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [{
    path: '/register',
    component: Register
  },
  {
    path: '/login',
    component: Login
  },
  {
    path: '/index',
    component: Index
  },
  {
    path: '/items',
    component: Items
  },
]

const router = new VueRouter({
  routes // short for `routes: routes`
})
// done vue router

// axios interceptors
axios.interceptors.request.use(function (config) {
  // Add our access token, if we have one, to each request
  if (store.getters.accessToken) {
    config.headers.Authorization = 'Bearer ' + store.getters.accessToken
  }
  return config
}, function (error) {
  // Do something with request error
  return Promise.reject(error)
})

// Add a response interceptor
axios.interceptors.response.use(function (response) {
  // Do something with response data
  return response
}, function (error) {
  // Do something with response error
  if (error.response.status === 401) {
    store.commit('logout')
    router.push('login')
  }
  if (error.response.status === 403) {
    store.commit('logout')
    router.push('login')
  }
  if (error.response.status === 422) {
    store.commit('logout')
    router.push('login')
  }
  return Promise.reject(error)
})

// end axios interceptors
new Vue({
  render: h => h(App),
  router,
  store,
  beforeCreate() {
    this.$store.commit('initStore');
  }
}).$mount('#app')
