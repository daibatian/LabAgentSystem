// 仅供页面 <script> 中 setup 函数使用
import { ref } from 'vue'
import { getUserInfo, setToken, setUserInfo } from './auth'

const userInfo = ref(getUserInfo()) // 响应式对象，可以更新最新的值

export function useUser() {
  function saveLoginData(data) {
    setToken(data.token)
    setUserInfo(data.user)
    userInfo.value = data.user // 更新响应式对象的值
  }

  function updateUser(user) {
    setUserInfo(user)
    userInfo.value = user // 更新响应式对象的值
  }

  function reloadUser() {
    userInfo.value = getUserInfo() // 重新获取用户信息并更新响应式对象的值
  }

  return { userInfo, saveLoginData, updateUser, reloadUser }
}
