import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import PullRequests from '../views/PullRequests.vue'
import GitHubAnalysis from '../views/GitHubAnalysis.vue'
import AIAnalysis from '../views/AIAnalysis.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/prs',
    name: 'PullRequests',
    component: PullRequests
  },
  {
    path: '/github',
    name: 'GitHubAnalysis',
    component: GitHubAnalysis
  },
  {
    path: '/ai',
    name: 'AIAnalysis',
    component: AIAnalysis
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router