import axios from 'axios'
import { getToken, logout } from './auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 在请求发送之前做一些处理
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (res) => {
    const data = res.data
    console.log(data)
    if (data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      if (data.code === 401) {
        // 处理未授权的情况，例如跳转到登录页
        logout()
        router.push('/login')
        return Promise.reject(data)
      }
    }
    return data
  },
  (error) => {
    if (error.response) {
      const httpStatusCode = error.response.status
      if (httpStatusCode === 401) {
        ElMessage.error('登录状态已失效，请重新登录')
        logout()
        router.push('/login')
      } else {
        ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络异常，请检查后端服务')
    }
    return Promise.reject(error)
  }
)

export default service
