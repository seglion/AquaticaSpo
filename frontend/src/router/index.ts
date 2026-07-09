import { createRouter, createWebHistory } from 'vue-router'
import { useAccessStore } from '../stores/access.store'

// Layouts
import AuthLayout from '../components/templates/AuthLayout.vue'
import DashboardLayout from '../components/templates/DashboardLayout.vue'

// Views (Lazy loaded)
const LoginView = () => import('../views/LoginView.vue')
const DashboardView = () => import('../views/DashboardView.vue')


const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            component: AuthLayout,
            children: [
                {
                    path: '',
                    name: 'login',
                    component: LoginView
                }
            ]
        },
        {
            path: '/',
            component: DashboardLayout,
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    redirect: { name: 'dashboard' }
                },
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: DashboardView
                }
            ]
        }
    ]
})

router.beforeEach((to, _from, next) => {
    const accessStore = useAccessStore()

    if (to.meta.requiresAuth && !accessStore.isAuthenticated) {
        next({ name: 'login' })
    } else if (to.name === 'login' && accessStore.isAuthenticated) {
        next({ name: 'dashboard' })
    } else {
        next()
    }
})

export default router
