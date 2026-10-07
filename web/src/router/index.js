import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Evaluation from '../views/Evaluation.vue'
import Analytics from '../views/Analytics.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/evaluation', name: 'Evaluation', component: Evaluation },
  { path: '/analytics', name: 'Analytics', component: Analytics }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  if (to.meta.public) return next()
  if (!localStorage.getItem('access_token')) return next('/login')
  next()
})

export default router
